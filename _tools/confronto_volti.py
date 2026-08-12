#!/usr/bin/env python3
"""Affianca le fotografie vere e il ritratto generato ALLA STESSA ALTEZZA DI TESTA.

    python3 _tools/confronto_volti.py --uscita confronto.png \\
        "A1.jpg:0.20,0.05,0.70,0.55=VERA A1" \\
        "madre.png:0.28,0.03,0.75,0.66=GENERATO"

Ogni argomento e' `file:x0,y0,x1,y1=etichetta`, con i quattro numeri espressi
in FRAZIONI del lato (0-1): sono il riquadro del volto, dalla cima dei capelli
al mento. I ritagli si portano tutti alla stessa altezza, cosi' si confrontano
i lineamenti e non le dimensioni.

⛔ 12 agosto 2026 — perche' esiste. Un ritratto madre era stato giudicato
"vicino" guardandolo da solo. Affiancato alla fotografia vera alla stessa
altezza di testa sono saltate fuori quattro derive in dieci secondi, tutte nella
stessa direzione: lineamenti regolarizzati e simmetria quasi perfetta. Il
confronto affiancato non e' un vezzo: e' l'unico modo in cui le derive si
vedono. Da solo, un volto sintetico sembra sempre giusto.

⚠️ Chi decide se e' la persona e' chi la CONOSCE. Questo strumento prepara il
confronto, non lo giudica.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

CARATTERI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caratteri")
ALTEZZA = 760          # altezza comune dei ritagli
MARGINE = 20
TITOLO = 54


def carattere(punti):
    for nome in ("montserrat-700-latin.ttf", "Montserrat-Bold.ttf"):
        p = os.path.join(CARATTERI, nome)
        if os.path.exists(p):
            return ImageFont.truetype(p, punti)
    return ImageFont.load_default()


def pezzo(spec):
    """`file:x0,y0,x1,y1=etichetta` → (immagine ritagliata, etichetta)."""
    testo, _, etichetta = spec.partition("=")
    percorso, _, box = testo.rpartition(":")
    if not percorso:
        percorso, box = testo, ""
    im = Image.open(os.path.expanduser(percorso)).convert("RGB")
    if box:
        try:
            x0, y0, x1, y1 = (float(v) for v in box.split(","))
        except ValueError:
            sys.exit(f"⛔ riquadro illeggibile in: {spec}")
        im = im.crop((int(x0 * im.width), int(y0 * im.height),
                      int(x1 * im.width), int(y1 * im.height)))
    im = im.resize((max(1, int(im.width * ALTEZZA / im.height)), ALTEZZA),
                   Image.LANCZOS)
    return im, (etichetta or os.path.basename(percorso))


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("pezzi", nargs="+", help="file:x0,y0,x1,y1=etichetta")
    p.add_argument("--uscita", required=True)
    a = p.parse_args()

    pezzi = [pezzo(s) for s in a.pezzi]
    larghezza = sum(i.width for i, _ in pezzi) + MARGINE * (len(pezzi) + 1)
    tela = Image.new("RGB", (larghezza, ALTEZZA + TITOLO + MARGINE * 2), (24, 24, 24))
    d = ImageDraw.Draw(tela)
    f = carattere(26)

    x = MARGINE
    for im, etichetta in pezzi:
        tela.paste(im, (x, TITOLO + MARGINE))
        colore = (255, 213, 128) if "GENERAT" in etichetta.upper() else (255, 255, 255)
        d.text((x + im.width // 2, TITOLO // 2 + 6), etichetta,
               font=f, fill=colore, anchor="mm")
        x += im.width + MARGINE

    fuori = os.path.expanduser(a.uscita)
    tela.save(fuori)
    print(f"  ✅ {fuori}  {tela.size}")


if __name__ == "__main__":
    main()
