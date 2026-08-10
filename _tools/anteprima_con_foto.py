#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L'ANTEPRIMA DI CONDIVISIONE CON LA FACCIA DI CHI FIRMA
======================================================
Genera la scheda 1200x630 che Facebook e WhatsApp mostrano quando qualcuno
incolla il link, mettendoci dentro la FOTOGRAFIA della persona che firma la
pagina, e la aggancia ai tre posti che contano: og:image, twitter:image e il
campo "image" del dato strutturato JSON-LD.

⭐ PERCHE' ESISTE, ACCANTO A anteprime_social.py (10 agosto 2026)
anteprime_social.py disegna una scheda di solo testo su fondo arancione: va
benissimo per una pagina di sezione, ma non per un articolo che UNA PERSONA
porta all'attenzione. Il 10 agosto la pagina delle riflessioni della prof.ssa
Trucco, firmata dal portavoce Luigi Spanu, mostrava su Facebook l'immagine del
PensAttivo: l'aveva ereditata dal tema Stabilicum. La faccia di chi firma e' il
motivo per cui un iscritto si ferma a leggere in un gruppo: va nella scheda.

⛔ IL RITAGLIO SI GUARDA, NON SI INDOVINA. Le foto dei dirigenti in images/
spesso NON sono fotografie nude: sono manifesti verticali gia' composti, con il
nome stampato sotto e l'intestazione sopra. Ritagliando a occhio ci finisce
mezza scritta. Si passa --ritaglio con le coordinate misurate sull'originale
(sinistra,alto,destra,basso) e si guarda il file prodotto prima di applicarlo.

    python3 _tools/anteprima_con_foto.py \
        --pagina stabilicum-intelligibilita-trucco-agosto2026.html \
        --foto images/spanu-audizione-stabilicum.webp \
        --ritaglio 172,200,727,960 \
        --occhiello "LUIGI SPANU PORTA ALL'ATTENZIONE" \
        --titolo "Si puo' votare una legge che non si riesce a capire?" \
        --sottotitolo "Le riflessioni della prof.ssa Lara Trucco sullo Stabilicum"
        # e --applica per scrivere davvero

Senza --titolo prende l'og:title della pagina.
"""
import argparse
import os
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARATTERI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caratteri")
DEST = os.path.join(REPO, "images", "anteprime")

L, H = 1200, 630
FOTO_L = 440                 # la colonna della fotografia, a destra
SFUMA = 150                  # quanto la foto sfuma dentro il fondo, a sinistra

# ⛔ LA SCHEDA NON SI GUARDA A 1200 PIXEL. Nel diario di Facebook esce larga
#    circa 500 px sul computer e 360 sul telefono: tutto quello che scriviamo
#    qui va diviso per due o per tre. Una riga da 20 px diventa 7 px e sparisce.
#    Regola presa il 10 agosto 2026, dopo che Fernando ha visto la prima prova:
#    niente sotto i 26 px, e si controlla sempre sulla prova rimpicciolita.
MINIMO = 26


def font(nome, dim):
    p = os.path.join(CARATTERI, nome + ".ttf")
    if os.path.exists(p):
        return ImageFont.truetype(p, dim)
    return ImageFont.load_default()


def titolo_della_pagina(html):
    m = re.search(r'<meta[^>]*property=["\']?og:title["\']?[^>]*content=["\']([^"\']+)', html)
    if not m:
        m = re.search(r"<title>(.*?)</title>", html, re.S)
    t = re.sub(r"<[^>]+>", "", m.group(1)) if m else ""
    for a, b in (("&mdash;", "—"), ("&rsquo;", "’"), ("&nbsp;", " "), ("&egrave;", "è"),
                 ("&agrave;", "à"), ("&eacute;", "é"), ("&ograve;", "ò"), ("&ugrave;", "ù"),
                 ("&#8217;", "’"), ("&amp;", "&"), ("&laquo;", "«"), ("&raquo;", "»")):
        t = t.replace(a, b)
    t = re.sub(r"\s*[|–—-]\s*(PA|Partecipazione Attiva)\b.*$", "", t)
    return re.sub(r"\s+", " ", t).strip()


def disegna(foto, ritaglio, occhiello, titolo, sottotitolo, dove):
    im = Image.new("RGB", (L, H), "#8a4e00")
    dr = ImageDraw.Draw(im)
    # la sfumatura del sito, la stessa di anteprime_social.py
    for y in range(H):
        k = y / H
        dr.line([(0, y), (L, y)],
                fill=(int(0x8a + (0xe8 - 0x8a) * k),
                      int(0x4e + (0x90 - 0x4e) * k),
                      int(0x00 + (0x0a - 0x00) * k)))

    # ---- la fotografia, colonna di destra, sfumata a sinistra
    ph = Image.open(os.path.join(REPO, foto)).convert("RGB")
    if ritaglio:
        ph = ph.crop(ritaglio)
    # riempio la colonna senza deformare: scalo sul lato piu' stretto e taglio
    k = max(FOTO_L / ph.width, H / ph.height)
    ph = ph.resize((max(1, round(ph.width * k)), max(1, round(ph.height * k))), Image.LANCZOS)
    sx = (ph.width - FOTO_L) // 2
    sy = (ph.height - H) // 2
    ph = ph.crop((sx, sy, sx + FOTO_L, sy + H))
    maschera = Image.new("L", (FOTO_L, H), 255)
    dm = ImageDraw.Draw(maschera)
    for x in range(SFUMA):                      # bordo sinistro che si dissolve
        dm.line([(x, 0), (x, H)], fill=int(255 * (x / SFUMA) ** 1.5))
    im.paste(ph, (L - FOTO_L, 0), maschera)

    # ⛔ LA VELATURA NON E' DECORAZIONE, E' LEGGIBILITA'. Il bianco
    #    sull'arancione del movimento sta intorno a 2:1 di contrasto: il titolo
    #    grande regge, l'occhiello e il sottotitolo no. Fernando li ha visti e
    #    ha detto «e' quasi illeggibile» (10 agosto 2026). Sotto la colonna del
    #    testo passa un velo bruno che porta il bianco oltre 7:1.
    velo = Image.new("RGBA", (L, H), (0, 0, 0, 0))
    dv = ImageDraw.Draw(velo)
    for x in range(L - FOTO_L + SFUMA):
        k = 1 - x / (L - FOTO_L + SFUMA)
        dv.line([(x, 0), (x, H)], fill=(46, 22, 2, int(215 * k ** 0.85)))
    im = Image.alpha_composite(im.convert("RGBA"), velo).convert("RGB")
    dr = ImageDraw.Draw(im)

    # ---- logo tondo in alto a sinistra
    logo_p = os.path.join(REPO, "LOGO-PA.webp")
    if os.path.exists(logo_p):
        lg = Image.open(logo_p).convert("RGBA").resize((104, 104), Image.LANCZOS)
        mk = Image.new("L", (104, 104), 0)
        ImageDraw.Draw(mk).ellipse((0, 0, 103, 103), fill=255)
        im.paste(lg, (66, 50), mk)
    # la riga «MOVIMENTO POPOLARE DEI CITTADINI ITALIANI» stava a 17 px: nel
    # diario diventava una sbavatura grigia. Tolta: il nome grande basta.
    dr.text((186, 78), "PARTECIPAZIONE ATTIVA",
            font=font("montserrat-900-latin", 34), fill="white")

    # ---- IL BLOCCO DI TESTO SI MISURA PRIMA DI SCRIVERLO, poi si centra.
    # Scrivendo riga per riga dall'alto, il 10 agosto 2026 il sottotitolo e'
    # finito sopra l'indirizzo del sito: due scritte una dentro l'altra. Qui si
    # calcola l'ingombro, si rimpicciolisce il titolo finche' ci sta dentro, e
    # solo allora si disegna.
    largh = L - FOTO_L - 20 - 72                # la colonna del testo, a sinistra
    ALTO, BASSO = 190, H - 120                  # fra l'intestazione e l'indirizzo

    def impagina(dim):
        b = []
        if occhiello:
            b.append(("occ", occhiello, font("montserrat-700-latin", MINIMO + 2), 76))
        f_t = font("merriweather-700-latin", dim)
        for r in textwrap.wrap(titolo, width=max(8, int(largh / (dim * 0.50))))[:4]:
            b.append(("tit", r, f_t, int(dim * 1.26)))
        if sottotitolo:
            # ⛔ 10 agosto 2026, Fernando: «questa parte va evidenziata al
            #    massimo». Il sottotitolo dice DI CHI sono le riflessioni: e' la
            #    riga che qualifica il contenuto, non una didascalia. Bianco
            #    pieno e neretto, come il titolo. (Il verde brillante sarebbe
            #    stato l'altra strada: scartato, sull'arancione stona e con la
            #    velatura scende sotto il bianco come contrasto.)
            f_s = font("montserrat-700-latin", MINIMO + 4)
            for i, r in enumerate(textwrap.wrap(
                    sottotitolo, width=max(8, int(largh / ((MINIMO + 4) * 0.60))))[:3]):
                b.append(("sub" + ("1" if i == 0 else ""), r, f_s, MINIMO + 16))
        return b

    for dim in (52, 48, 44, 40, 36, 32):
        blocco = impagina(dim)
        alto = sum(h for _, _, _, h in blocco) + (18 if sottotitolo else 0)
        if alto <= BASSO - ALTO:
            break
    y = ALTO + max(0, ((BASSO - ALTO) - alto) // 2)

    COLORE = {"occ": (255, 214, 140), "tit": "white", "sub": "white", "sub1": "white"}
    for tipo, testo, f, passo in blocco:
        if tipo == "sub1":
            y += 18                             # aria fra titolo e sottotitolo
        dr.text((72, y), testo, font=f, fill=COLORE[tipo])
        if tipo == "occ":
            dr.line([(72, y + 44), (72 + 110, y + 44)], fill=(255, 214, 140), width=4)
        y += passo

    dr.text((72, H - 86), "partecipazione-attiva.it",
            font=font("montserrat-900-latin", 32), fill="white")
    dr.rectangle([(0, H - 14), (L, H)], fill="#ffd580")

    os.makedirs(os.path.dirname(dove), exist_ok=True)
    im.save(dove, quality=88, optimize=True)
    return os.path.getsize(dove) // 1024


def aggancia(pagina, url, alt=""):
    """og:image, twitter:image e il campo image del JSON-LD: tutti e tre.
    Facebook legge og:image, ma il JSON-LD lasciato indietro rimette in giro
    l'immagine vecchia attraverso Google e l'anteprima della ricerca.

    Aggiunge anche og:image:alt, che descrive la scheda a chi naviga con un
    lettore di schermo: senza, la casella resta vuota (verificato il 10 agosto
    2026 nel debugger di Facebook, che la mostrava in bianco)."""
    p = os.path.join(REPO, pagina)
    d = open(p, encoding="utf-8").read()
    prima = d
    # ⛔ IL NOME DELLA PROPRIETA' VA CHIUSO. Senza il (?=["\'\s]) finale,
    #    "og:image" acchiappa anche og:image:width e og:image:height e ci
    #    scrive dentro l'indirizzo dell'immagine al posto di 1200 e 630.
    #    Sbagliato cosi' la prima volta, il 10 agosto 2026.
    d = re.sub(r'(property=["\']?og:image(?=["\'\s])["\']?[^>]*content=["\'])[^"\']*',
               lambda m: m.group(1) + url, d)
    d = re.sub(r'(name=["\']?twitter:image(?=["\'\s])["\']?[^>]*content=["\'])[^"\']*',
               lambda m: m.group(1) + url, d)
    d = re.sub(r'("image"\s*:\s*")[^"]*', lambda m: m.group(1) + url, d)
    if alt and "og:image:alt" not in d:
        d = re.sub(r'(<meta[^>]*property=["\']?og:image["\']?[^>]*>)',
                   lambda m: m.group(1) + f'<meta property=og:image:alt content="{alt}">',
                   d, count=1)
    if d != prima:
        open(p, "w", encoding="utf-8").write(d)
    return d != prima


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pagina", required=True)
    ap.add_argument("--foto", required=True)
    ap.add_argument("--ritaglio", default="", help="sinistra,alto,destra,basso sull'originale")
    ap.add_argument("--occhiello", default="")
    ap.add_argument("--titolo", default="")
    ap.add_argument("--sottotitolo", default="")
    ap.add_argument("--alt", default="", help="descrizione della scheda per i lettori di schermo")
    ap.add_argument("--versione", default="", help="suffisso nel nome del file: OBBLIGATORIO se la"
                                                   " scheda cambia dopo essere stata condivisa")
    ap.add_argument("--applica", action="store_true")
    a = ap.parse_args()

    html = open(os.path.join(REPO, a.pagina), encoding="utf-8").read()
    titolo = a.titolo or titolo_della_pagina(html)
    ritaglio = tuple(int(x) for x in a.ritaglio.split(",")) if a.ritaglio else None

    # ⛔ FACEBOOK TIENE IN CACHE L'IMMAGINE PER INDIRIZZO, non per contenuto.
    #    Il 10 agosto 2026 Fernando ha premuto «Esegui lo scraping di nuovo»
    #    dieci volte: i tag si aggiornavano (si vedeva og:image:alt comparire),
    #    l'immagine no, perche' il nome del file non era mai cambiato. Se la
    #    scheda cambia DOPO che il link e' gia' passato dal debugger, si cambia
    #    il nome: --versione 2 → ...-anteprima-v2.jpg. E' l'unico modo.
    nome = (a.pagina.replace(".html", "") + "-anteprima"
            + (f"-v{a.versione}" if a.versione else "") + ".jpg")
    dove = os.path.join(DEST if a.applica else os.environ.get("TMPDIR", "/tmp"), nome)
    kb = disegna(a.foto, ritaglio, a.occhiello, titolo, a.sottotitolo, dove)

    print(f"  🖼  {dove}  ({kb} KB)")
    if a.applica:
        url = "https://partecipazione-attiva.it/images/anteprime/" + nome
        alt = a.alt or " — ".join(x for x in (a.occhiello.capitalize(), titolo) if x)
        if aggancia(a.pagina, url, alt):
            print("  🔗 agganciata alla pagina")
        elif url in open(os.path.join(REPO, a.pagina), encoding="utf-8").read():
            # rigenerare la stessa scheda non cambia i tag: non e' un errore.
            print("  ✅ la pagina puntava gia' a questa scheda")
        else:
            print("  ⚠️  nessun campo immagine trovato nella pagina")
    else:
        print("  (prova a vuoto: guarda il file, poi rilancia con --applica)")


if __name__ == "__main__":
    main()
