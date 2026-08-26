#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
schema_coerente.py — la marcatura deve dire quello che dice la pagina.

Nasce il 26 agosto 2026 da un caso concreto: spanu-congresso-base-popolare.html
dichiarava a Google tre FAQ secondo cui «Base Popolare» era una proposta di legge
presentata alla Camera il 9 aprile. Erano i residui dell'articolo sul SIRE, copiato
per farne uno nuovo e ripulito solo a meta'. Lo stesso blocco stava, identico, su
altre cinque pagine che di SIRE non parlano.

Controlla, su ogni pagina .html della radice:

  1. INDIRIZZI  canonical, og:url e hreflang devono nominare la pagina stessa
  2. IMMAGINI   ogni immagine dichiarata (og:image, image del JSON-LD) deve esistere
  3. FAQ        le parole forti delle risposte (nomi propri, sigle, numeri, date)
                devono comparire nel testo visibile della pagina
  4. DATE       datePublished deve coincidere con la data stampata nell'articolo

Uso:
    python3 _tools/schema_coerente.py            tutte le pagine
    python3 _tools/schema_coerente.py PAGINA.html
    python3 _tools/schema_coerente.py --silenzioso   stampa solo i problemi

Esce con codice 1 se trova almeno una segnalazione: si puo' mettere in un hook.
"""
import re, json, sys, glob, os, html, unicodedata

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITO = "partecipazione-attiva.it"

MESI = {"gennaio":1,"febbraio":2,"marzo":3,"aprile":4,"maggio":5,"giugno":6,
        "luglio":7,"agosto":8,"settembre":9,"ottobre":10,"novembre":11,"dicembre":12}

# parole che sembrano nomi propri ma non aggiungono niente al controllo
FERMATE = {"Partecipazione","Attiva","Camera","Deputati","Italia","Stato","Roma",
           "Napoli","Governo","Parlamento","Costituzione","Google","YouTube","Facebook",
           "Il","La","Le","Lo","Gli","Un","Una","Non","Che","Chi","Come","Quando","Dove",
           "Perche","Perché","Secondo","Nel","Nella","Dal","Della","Del","Con","Per","Sono","Si","E","A"}


def testo_visibile(sorgente: str) -> str:
    """Il testo che un lettore vede: niente script, niente stile, niente tag."""
    m = re.search(r"<main[^>]*>(.*?)</main>", sorgente, re.S)
    corpo = m.group(1) if m else sorgente
    corpo = re.sub(r"<script.*?</script>|<style.*?</style>", " ", corpo, flags=re.S)
    corpo = re.sub(r"<[^>]+>", " ", corpo)
    corpo = html.unescape(corpo)
    return re.sub(r"\s+", " ", corpo)


def senza_accenti(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def blocchi_jsonld(sorgente: str):
    for m in re.finditer(r'<script type=["\']?application/ld\+json["\']?>(.*?)</script>',
                         sorgente, re.S):
        try:
            d = json.loads(m.group(1))
        except Exception as e:
            yield ("__ROTTO__", str(e))
            continue
        for obj in (d if isinstance(d, list) else [d]):
            if isinstance(obj, dict):
                yield (obj.get("@type"), obj)


def parole_forti(frase: str):
    """Sigle, numeri, date e nomi propri: le cose che si possono verificare."""
    fuori = []
    for p in re.findall(r"\b[A-Z]{3,}\b", frase):                 # sigle: SIRE, AGENAS
        fuori.append(p)
    for p in re.findall(r"\b\d{1,4}(?:[.,]\d+)?%?\b", frase):     # numeri e anni
        if len(p) > 1:
            fuori.append(p)
    for p in re.findall(r"\b[A-ZÀ-Ú][a-zà-ú]{2,}(?: [A-ZÀ-Ú][a-zà-ú]{2,})+", frase):
        fuori.append(p)                                            # nomi e cognomi
    return [p for p in dict.fromkeys(fuori) if p not in FERMATE]


def compare(parola: str, piatto: str) -> bool:
    """Una sigla o un numero si cercano tali e quali; un nome composto basta che
    la pagina ne nomini almeno un pezzo — «Stefano Piva» e «Stefano Francesco
    Piva» sono la stessa persona, e un controllo che li distingue e' rumore."""
    p = senza_accenti(parola).lower()
    if " " not in p:
        return p in piatto
    return any(pezzo in piatto for pezzo in p.split())


def data_stampata(testo: str):
    """La data di pubblicazione e' quella del badge 📅 accanto alla firma. La prima
    data del testo non va bene: negli annunci e' quella dell'evento, che viene dopo."""
    m = re.search("\U0001F4C5[^0-9]{0,12}(\\d{1,2})\\s+(" + "|".join(MESI) + ")\\s+(\\d{4})",
                  testo, re.I)
    if not m:
        return None
    return "%s-%02d-%02d" % (m.group(3), MESI[m.group(2).lower()], int(m.group(1)))


def controlla(nome: str):
    sorgente = open(os.path.join(RADICE, nome), encoding="utf-8").read()
    visibile = testo_visibile(sorgente)
    # per le FAQ si guarda la pagina intera: il nome per esteso del movimento e la
    # Costituzione stanno nel pie' di pagina, fuori da <main>, e non sono un errore
    piatto = senza_accenti(testo_visibile(re.sub(r"</?main[^>]*>", "", sorgente))).lower()
    guai = []

    # 1 — indirizzi (template.html e' lo stampo, non una pagina del sito)
    atteso = "index.html" if nome == "index.html" else nome
    for etichetta, rx in (("canonical", r'rel=["\']?canonical["\']?\s+href=["\']?([^"\' >]+)'),
                          ("og:url",    r'og:url"\s*content="([^"]+)"'),
                          ("hreflang",  r'hreflang="it"\s+href="([^"]+)"')):
        m = re.search(rx, sorgente)
        if not m:
            continue
        base = os.path.basename(m.group(1).rstrip("/")) or "index.html"
        if base == SITO:
            base = "index.html"
        if base != atteso and nome != "template.html":
            guai.append(f"{etichetta} nomina {base}, ma la pagina e' {nome}")

    # 2 — immagini dichiarate
    urls = set(re.findall(r'og:image"\s*content="([^"]+)"', sorgente))
    for _, obj in blocchi_jsonld(sorgente):
        if isinstance(obj, dict):
            for chiave in ("image", "thumbnailUrl", "contentUrl"):
                v = obj.get(chiave)
                if isinstance(v, str) and SITO in v:
                    urls.add(v)
    for u in urls:
        rel = u.split(SITO + "/", 1)[-1].split("?")[0]
        if rel and not os.path.exists(os.path.join(RADICE, rel)):
            guai.append(f"immagine dichiarata ma assente sul disco: {rel}")

    # 3 — FAQ contro il testo visibile
    for tipo, obj in blocchi_jsonld(sorgente):
        if tipo == "__ROTTO__":
            guai.append(f"blocco JSON-LD illeggibile: {obj}")
            continue
        if tipo != "FAQPage":
            continue
        for q in obj.get("mainEntity", []):
            domanda = q.get("name", "")
            risposta = q.get("acceptedAnswer", {}).get("text", "")
            assenti = [p for p in parole_forti(domanda + " " + risposta)
                       if not compare(p, piatto)]
            if assenti:
                guai.append("FAQ «%s»: nella pagina non compaiono %s"
                            % (domanda[:60], ", ".join(assenti[:6])))

    # 4 — datePublished contro la data stampata
    for tipo, obj in blocchi_jsonld(sorgente):
        if tipo in ("NewsArticle", "Article", "BlogPosting") and isinstance(obj, dict):
            dp = obj.get("datePublished", "")[:10]
            stampata = data_stampata(visibile[:2500])
            if dp and stampata and dp != stampata:
                guai.append(f"datePublished dice {dp}, ma l'articolo stampa {stampata}")
    return guai


def scheletro(frase: str) -> str:
    """La frase senza i nomi propri e senza i numeri. Serve perche' la contaminazione
    sopravvive al trova-e-sostituisci: su spanu-congresso-base-popolare.html «SIRE»
    era stato cambiato in «Congresso Base Popolare» e il resto della frase — falso —
    era rimasto identico alle altre sei pagine."""
    f = re.sub(r"\b[A-ZÀ-Ú][\w'à-ú]*\b", "§", frase)
    f = re.sub(r"\d+", "#", f)
    return re.sub(r"[^a-zà-ú ]+", " ", f.lower()).strip()


def risposte_ripetute(pagine):
    """Il segnale piu' netto della contaminazione: la stessa risposta, o la stessa
    frase con i soli nomi cambiati, su tre o piu' pagine che raccontano cose diverse.
    E' cosi' che il blocco del SIRE e' finito su sette articoli che di SIRE non parlano."""
    dove = {}
    for nome in pagine:
        sorgente = open(os.path.join(RADICE, nome), encoding="utf-8").read()
        for tipo, obj in blocchi_jsonld(sorgente):
            if tipo != "FAQPage" or not isinstance(obj, dict):
                continue
            for q in obj.get("mainEntity", []):
                t = q.get("acceptedAnswer", {}).get("text", "").strip()
                if len(t) > 60:
                    dove.setdefault(scheletro(t), set()).add((nome, t))
    return {sorted(v)[0][1]: sorted({n for n, _ in v}) for v in dove.values()
            if len({n for n, _ in v}) >= 3}


def main():
    argomenti = [a for a in sys.argv[1:] if not a.startswith("--")]
    silenzioso = "--silenzioso" in sys.argv
    pagine = argomenti or sorted(os.path.basename(p) for p in glob.glob(os.path.join(RADICE, "*.html")))
    totale = 0
    for nome in pagine:
        guai = controlla(nome)
        totale += len(guai)
        if guai:
            print(f"\n⚠ {nome}")
            for g in guai:
                print("   ·", g)
        elif not silenzioso:
            print(f"✓ {nome}")
    if len(pagine) > 3:
        ripetute = risposte_ripetute(pagine)
        for t, dv in ripetute.items():
            totale += 1
            print(f"\n⚠ stessa risposta su {len(dv)} pagine: {', '.join(dv)}")
            print("   ·", t[:150] + ("…" if len(t) > 150 else ""))

    print(f"\n{len(pagine)} pagine controllate, {totale} segnalazioni")
    return 1 if totale else 0


if __name__ == "__main__":
    sys.exit(main())
