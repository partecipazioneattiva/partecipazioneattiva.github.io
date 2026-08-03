#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wireframe di impaginazione per il manifesto elettorale.

Non genera grafica: genera lo SCHEMA da allegare al generatore di immagini
(Gemini / Nano Banana) come terza immagine di riferimento.

Perche' esiste (3 agosto 2026). Descrivere l'impaginazione a parole non basta:
«la figura occupa i due terzi» viene ignorato, «riempi la colonna» fa duplicare
il testo. Nano Banana invece legge gli schizzi: un wireframe con i blocchi al
posto giusto vincola la composizione molto meglio di qualunque frase.
Dettagli in MANUALE_GEMINI_IMMAGINI_v1.md §11bis, trucco 1.

Uso:
    python3 _tools/layout_manifesto.py --uscita layout.png
    (poi si allega layout.png insieme a ritratto e logo, dicendo al modello
     che serve SOLO come schema di impaginazione)
"""

import argparse
import os

from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

PERGAMENA = (243, 231, 205)
BLOCCO    = (176, 176, 176)
FIGURA    = (110, 110, 110)
PANORAMA  = (208, 220, 228)
ORO       = (176, 124, 42)
TESTO     = (40, 40, 40)


def font(dim):
    try:
        return ImageFont.truetype(FONT, dim)
    except OSError:
        return ImageFont.load_default()


def etichetta(dr, x, y, w, h, testo, dim, muto):
    """Blocco grigio. MUTO di default: il 3 agosto 2026 Nano Banana ha letto le
    etichette dello schema come testo da stampare e sul manifesto sono comparsi
    i titoletti CARICA, TERRITORI, VALORI. Uno schema di impaginazione non deve
    contenere parole: le posizioni bastano, i contenuti stanno nel prompt.
    Con --etichette torna la versione parlante, che serve solo a noi per capirlo."""
    dr.rectangle((x, y, x + w, y + h), fill=BLOCCO)
    if not muto and testo:
        dr.text((x + w // 2, y + h // 2), testo, font=font(dim), fill=TESTO, anchor="mm")


def elettorale(W, H, muto=True):
    """Lo schema del manifesto elettorale VERO, non della locandina.

    Gerarchia imposta dalla pratica italiana (Venturini, Italgrafica, e i
    manifesti che si vedono per strada): il volto domina, il nome e' secondo
    solo alla faccia, lo slogan sta in 3-7 parole, poi simbolo di lista, data e
    committente. Tutto il resto e' rumore: si legge a 30 metri, in un secondo.

    Quote (frazioni dell'altezza):
      0.00-0.56  volto/mezzo busto a tutta larghezza
      0.56-0.70  NOME e COGNOME
      0.70-0.76  carica e territori
      0.76-0.84  slogan
      0.84-0.93  simbolo di lista + istruzione di voto
      0.93-1.00  data e committente
    """
    tela = Image.new("RGB", (W, H), PERGAMENA)
    dr = ImageDraw.Draw(tela)
    m = int(W * 0.06)
    larg = W - 2 * m

    # 1. il volto: fascia superiore piena, testa centrata e grande
    dr.rectangle((0, 0, W, int(H * 0.56)), fill=PANORAMA)
    cx = int(W * 0.50)
    dr.ellipse((cx - int(W * 0.19), int(H * 0.06), cx + int(W * 0.19), int(H * 0.36)),
               fill=FIGURA)                                        # testa
    dr.rounded_rectangle((cx - int(W * 0.34), int(H * 0.32), cx + int(W * 0.34),
                          int(H * 0.56)), radius=int(W * 0.05), fill=FIGURA)
    if not muto:
        dr.text((cx, int(H * 0.45)), "VOLTO GRANDE", font=font(int(W * 0.032)),
                fill=(240, 240, 240), anchor="mm")

    d = int(W * 0.020)
    quote = [
        (0.585, 0.055, "NOME", 0.92),
        (0.645, 0.055, "COGNOME", 0.92),
        (0.712, 0.026, "carica", 0.66),
        (0.746, 0.020, "territori", 0.78),
        (0.790, 0.048, "SLOGAN (3-7 parole)", 1.0),
        (0.935, 0.018, "data", 0.34),
        (0.962, 0.016, "committente", 0.62),
    ]
    for y_rel, h_rel, testo, w_rel in quote:
        etichetta(dr, m, int(H * y_rel), int(larg * w_rel), int(H * h_rel),
                  testo, d, muto)

    # 2. simbolo di lista a sinistra, istruzione di voto a destra
    lato = int(H * 0.085)
    dr.ellipse((m, int(H * 0.845), m + lato, int(H * 0.845) + lato), fill=BLOCCO)
    etichetta(dr, m + lato + int(W * 0.03), int(H * 0.862),
              larg - lato - int(W * 0.03), int(H * 0.050),
              "COME SI VOTA", d, muto)

    # 3. filo dorato di chiusura sopra il piede
    dr.rectangle((0, int(H * 0.925), W, int(H * 0.925) + max(3, int(W * 0.004))),
                 fill=ORO)
    return tela


def costruisci(W, H, muto=True):
    tela = Image.new("RGB", (W, H), PANORAMA)
    dr = ImageDraw.Draw(tela)

    x_col = int(W * 0.545)
    margine = int(W * 0.052)
    larg = x_col - 2 * margine

    # figura: testa a un quarto dall'alto, scende fino al bordo inferiore
    fx, fy = x_col - int(W * 0.06), int(H * 0.24)
    dr.ellipse((fx + int(W * 0.10), fy, fx + int(W * 0.30), fy + int(H * 0.16)),
               fill=FIGURA)                                     # testa
    dr.rounded_rectangle((fx, fy + int(H * 0.14), W, H), radius=int(W * 0.06),
                         fill=FIGURA)                           # spalle e busto
    if not muto:
        dr.text((fx + int(W * 0.20), int(H * 0.62)), "CANDIDATO",
                font=font(int(W * 0.030)), fill=(240, 240, 240), anchor="mm")

    # colonna pergamena
    dr.rectangle((0, 0, x_col, H), fill=PERGAMENA)
    dr.rectangle((x_col, 0, x_col + int(W * 0.008), H), fill=ORO)

    # blocchi distribuiti su TUTTA l'altezza: e' il senso dello schema
    d = int(W * 0.022)
    quote = [
        (0.030, 0.115, "LOGO", 0.42),
        (0.175, 0.075, "NOME", 1.0),
        (0.255, 0.075, "COGNOME", 1.0),
        (0.350, 0.008, "", 0.34),
        (0.385, 0.085, "CARICA (2 righe)", 1.0),
        (0.500, 0.075, "TERRITORI (2 righe)", 1.0),
        (0.605, 0.038, "ELEZIONI 2027", 0.85),
        (0.675, 0.006, "", 0.22),
        (0.705, 0.070, "VALORI (2 righe)", 0.95),
        (0.805, 0.035, "SITO", 0.70),
        (0.930, 0.022, "COMMITTENTE", 0.85),
    ]
    for y_rel, h_rel, testo, w_rel in quote:
        y, h = int(H * y_rel), int(H * h_rel)
        w = int(larg * w_rel)
        if not testo:                                   # i fili dorati
            dr.rectangle((margine, y, margine + w, y + h), fill=ORO)
        else:
            etichetta(dr, margine, y, w, h, testo, d, muto)

    return tela


def main():
    p = argparse.ArgumentParser(description="Wireframe di impaginazione del manifesto")
    p.add_argument("--larghezza", type=int, default=1400)
    p.add_argument("--rapporto", default="7:10", help="es. 7:10, 3:4, 4:5")
    p.add_argument("--stile", choices=("elettorale", "laterale"), default="elettorale",
                   help="elettorale = volto grande e slogan (default); laterale = colonna di testo")
    p.add_argument("--etichette", action="store_true",
                   help="scrive i nomi nei blocchi: solo per capirlo noi, MAI da allegare")
    p.add_argument("--uscita", required=True)
    a = p.parse_args()

    rw, rh = (float(n) for n in a.rapporto.split(":"))
    W = a.larghezza
    H = int(W * rh / rw)
    schema = elettorale if a.stile == "elettorale" else costruisci
    schema(W, H, muto=not a.etichette).save(os.path.expanduser(a.uscita))
    print("layout:", a.uscita, (W, H))


if __name__ == "__main__":
    main()
