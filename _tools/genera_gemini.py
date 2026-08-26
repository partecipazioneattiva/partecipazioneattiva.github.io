#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera l'immagine di un candidato chiamando l'API di Gemini dal Mac.

    python3 _tools/genera_gemini.py --elenca
    python3 _tools/genera_gemini.py --candidato rosa --foto A1 A4
    python3 _tools/genera_gemini.py --candidato luigi --stile card

⭐ PERCHE' DALL'API E NON DAL BROWSER (4 agosto 2026)
L'app Gemini stampa la stellina sulle immagini, e su AI Studio i modelli di
immagine sono dietro l'abbonamento. La chiave API invece dà il *free tier*
senza attivare nessuna fatturazione, e l'immagine che torna non ha filigrana
visibile (resta SynthID, invisibile: e' giusto che ci sia, e noi dichiariamo
comunque che l'immagine e' generata con IA).

⛔ LA CHIAVE NON STA IN QUESTO REPOSITORY, che e' pubblico. Sta in
    ~/.config/pa/gemini.key      (chmod 600)
oppure nella variabile d'ambiente GEMINI_API_KEY. Se finisce in un commit va
revocata subito da aistudio.google.com, non basta cancellarla dal file.
"""
import argparse
import base64
import json
import mimetypes
import os
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://generativelanguage.googleapis.com/v1beta"
CHIAVE = "~/.config/pa/gemini.key"
DATI = "~/Desktop/ARCHIVIO GENERALE/Claude IA/04_MANIFESTI_E_CARD/GEMINI LAVORI/candidati_manifesto.json"
LAVORI = "~/Desktop/ARCHIVIO GENERALE/Claude IA/04_MANIFESTI_E_CARD/GEMINI LAVORI"
QUI = os.path.dirname(os.path.abspath(__file__))


def chiave():
    k = os.environ.get("GEMINI_API_KEY")
    if k:
        return k.strip()
    p = os.path.expanduser(CHIAVE)
    if os.path.exists(p):
        return open(p, encoding="utf-8").read().strip()
    sys.exit(f"⛔ chiave non trovata. Scriverla in {CHIAVE} (chmod 600) "
             f"o esportare GEMINI_API_KEY.")


def chiama(percorso, corpo=None):
    url = f"{API}/{percorso}{'&' if '?' in percorso else '?'}key={chiave()}"
    dati = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(
        url, data=dati, method="POST" if corpo is not None else "GET",
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.load(r)
    except urllib.error.HTTPError as ex:
        testo = ex.read().decode(errors="replace")
        try:
            msg = json.loads(testo)["error"]["message"]
        except Exception:
            msg = testo[:400]
        sys.exit(f"⛔ l'API ha risposto {ex.code}: {msg}")


def elenca():
    """I modelli che questa chiave puo' davvero usare per le immagini."""
    d = chiama("models?pageSize=200")
    righe = []
    for m in d.get("models", []):
        nome = m["name"].split("/")[-1]
        if "image" in nome or "imagen" in nome:
            righe.append((nome, m.get("description", "")[:70]))
    if not righe:
        sys.exit("⛔ nessun modello di immagini disponibile per questa chiave.")
    print("Modelli di immagini disponibili con questa chiave:\n")
    for nome, desc in sorted(righe):
        print(f"  {nome:<38} {desc}")
    print("\nSi sceglie con --modello.")


def prompt_di(candidato, stile):
    """Il prompt lo scrive crea_prompt_manifesto.py: qui non si duplica nulla,
    o le due strade divergono e una delle due sbaglia l'istruzione di voto."""
    out = subprocess.run(
        [sys.executable, os.path.join(QUI, "crea_prompt_manifesto.py"),
         "--candidato", candidato, "--stile", stile],
        capture_output=True, text=True)
    if out.returncode:
        sys.exit(out.stderr.strip() or "⛔ crea_prompt_manifesto.py ha fallito")
    return out.stdout.strip()


def foto_di(c, quali):
    cartella = os.path.join(os.path.expanduser(LAVORI),
                            *c["cartella_foto"].split("/")[1:])
    if not os.path.isdir(cartella):
        sys.exit(f"⛔ cartella foto non trovata: {cartella}")
    trovate = []
    for f in sorted(os.listdir(cartella)):
        base, est = os.path.splitext(f)
        if est.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        etichetta = base.split("_")[0].upper()
        if quali and etichetta not in [q.upper() for q in quali]:
            continue
        if not quali and not etichetta.startswith("A"):
            continue
        trovate.append(os.path.join(cartella, f))
    if not trovate:
        sys.exit(f"⛔ nessuna foto in {cartella} (chieste: {quali or 'A*'})")
    return trovate


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--candidato")
    p.add_argument("--stile", default="card-vuota",
                   choices=["card-vuota", "card", "affissione"])
    p.add_argument("--modello", default="gemini-2.5-flash-image",
                   help="default: gemini-2.5-flash-image (Nano Banana). "
                        "--elenca dice quali accetta la chiave")
    p.add_argument("--foto", nargs="*", help="quali riferimenti (es. A1 A4). "
                                             "Default: tutti gli A*")
    p.add_argument("--proporzioni", default="2:3")
    p.add_argument("--uscita")
    p.add_argument("--dati", default=DATI)
    p.add_argument("--elenca", action="store_true", help="i modelli disponibili")
    a = p.parse_args()

    if a.elenca:
        return elenca()
    if not a.candidato:
        sys.exit("⛔ serve --candidato (o --elenca)")

    d = json.load(open(os.path.expanduser(a.dati), encoding="utf-8"))
    k = a.candidato.lower()
    if k not in d["candidati"]:
        sys.exit(f"⛔ '{k}' non c'e'. Disponibili: {', '.join(d['candidati'])}")
    c = d["candidati"][k]

    testo = prompt_di(k, a.stile)
    foto = foto_di(c, a.foto)
    print(f"riferimenti: {', '.join(os.path.basename(f) for f in foto)}",
          file=sys.stderr)

    parti = []
    for f in foto:
        parti.append({"inline_data": {
            "mime_type": mimetypes.guess_type(f)[0] or "image/jpeg",
            "data": base64.b64encode(open(f, "rb").read()).decode()}})
    parti.append({"text": testo})

    corpo = {"contents": [{"parts": parti}],
             "generationConfig": {"responseModalities": ["IMAGE"],
                                  "imageConfig": {"aspectRatio": a.proporzioni}}}
    r = chiama(f"models/{a.modello}:generateContent", corpo)

    immagini = [pt["inlineData"]["data"]
                for cand in r.get("candidates", [])
                for pt in cand.get("content", {}).get("parts", [])
                if "inlineData" in pt]
    if not immagini:
        motivo = (r.get("candidates") or [{}])[0].get("finishReason", "?")
        sys.exit(f"⛔ nessuna immagine nella risposta (finishReason: {motivo}). "
                 f"Se e' un blocco di sicurezza, si rigenera: il prompt chiede "
                 f"una fotografia, non contenuto politico.")

    uscita = os.path.expanduser(
        a.uscita or f"~/Desktop/{k}_{a.stile.replace('-', '_')}.png")
    open(uscita, "wb").write(base64.b64decode(immagini[0]))
    print(f"scritto: {uscita}")
    if a.stile == "card-vuota":
        print(f"\nora il testo:\n  python3 _tools/carta_social.py "
              f"--immagine {uscita} --candidato {k}", file=sys.stderr)


if __name__ == "__main__":
    main()
