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

    🔴 RIFATTO IL 4 AGOSTO 2026 sui due manifesti veri portati da Fernando —
    Salini (Forza Italia, europee 2024) e Bulbi (PD, politiche 2022). La prima
    versione divideva la tela in due fasce, foto sopra e testo sotto: e' il
    modo in cui si impagina una LOCANDINA. Nei manifesti veri non succede mai.

    Le quattro differenze, tutte misurate su quei due:

    1. LA FIGURA E' A TUTTA ALTEZZA e il testo le sta SOPRA. Nessuna fascia
       separata: il fondo e' uno solo.
    2. LA DATA STA IN ALTO ED E' GRANDE, seconda solo al volto e al cognome.
       Prima era penultima e minuscola. Su Salini "8-9 GIUGNO" e' in giallo,
       alto come il titolo; su Bulbi la data e' nella fascia rossa di testa.
    3. L'ISTRUZIONE DI VOTO E' DISEGNATA, non scritta: Salini mette la X
       tracciata SOPRA il simbolo. A trenta metri un segno si capisce, una
       frase no.
    4. IL COMMITTENTE E' UNA STRISCIA VERTICALE SUL BORDO, in corpo minimo:
       non occupa una riga dell'impaginato (Salini, bordo sinistro).

    E si e' tolta una riga: carica e territorio stanno insieme, perche' "X
    Municipalita'" da solo non lo capisce nessuno e due righe separate a
    trenta metri non si leggono comunque.

    Quote (frazioni dell'altezza), colonna di testo a destra:
      0.055-0.20  ELEZIONI + DATA, grandi, in alto
      0.60-0.665  slogan (3-7 parole)
      0.685-0.825 NOME e COGNOME (il cognome e' il piu' grande)
      0.834-0.864 carica e territorio, una riga sola
      0.888-0.948 istruzione di voto, due righe piccole
    Sul lato sinistro: simbolo di lista con la X, e committente in verticale.

    ⚠️ L'istruzione di voto sta IN FONDO, allineata al simbolo, non prima del
    cognome. Su Salini precede il cognome perche' li' il cognome si SCRIVE
    sulla scheda; nelle Municipalita' di Napoli il voto disgiunto e' escluso e
    si barra solo il simbolo, quindi l'istruzione punta al simbolo e gli sta
    accanto.
    """
    tela = Image.new("RGB", (W, H), PANORAMA)
    dr = ImageDraw.Draw(tela)

    # 1. la figura occupa TUTTA l'altezza, spostata a sinistra: il testo le va sopra
    cx = int(W * 0.31)
    dr.ellipse((cx - int(W * 0.20), int(H * 0.05), cx + int(W * 0.20), int(H * 0.35)),
               fill=FIGURA)                                        # testa
    dr.rounded_rectangle((int(W * 0.01), int(H * 0.31), int(W * 0.64), H),
                         radius=int(W * 0.06), fill=FIGURA)        # spalle e busto
    if not muto:
        dr.text((cx, int(H * 0.50)), "VOLTO A TUTTA ALTEZZA",
                font=font(int(W * 0.026)), fill=(240, 240, 240), anchor="mm")

    d = int(W * 0.020)
    xr = int(W * 0.50)                      # inizio della colonna di testo
    larg = W - xr - int(W * 0.05)

    quote = [
        (0.055, 0.070, "ELEZIONI (riga 1)", 1.00),
        (0.132, 0.070, "DATA — grande", 0.78),
        (0.600, 0.065, "SLOGAN (3-7 parole)", 1.00),
        (0.685, 0.048, "NOME", 0.55),
        (0.738, 0.087, "COGNOME — il piu' grande", 1.00),
        (0.834, 0.030, "carica · territorio", 1.00),
        (0.888, 0.026, "come si vota (riga 1)", 0.88),
        (0.922, 0.026, "come si vota (riga 2)", 0.94),
    ]
    for y_rel, h_rel, testo, w_rel in quote:
        etichetta(dr, xr, int(H * y_rel), int(larg * w_rel), int(H * h_rel),
                  testo, d, muto)

    # 2. simbolo di lista in basso a sinistra, con la X dell'istruzione di voto
    lato = int(H * 0.115)
    sx, sy = int(W * 0.06), int(H * 0.855)
    dr.ellipse((sx, sy, sx + lato, sy + lato), fill=BLOCCO)
    spessore = max(3, int(W * 0.006))
    dr.line((sx, sy, sx + lato, sy + lato), fill=TESTO, width=spessore)
    dr.line((sx + lato, sy, sx, sy + lato), fill=TESTO, width=spessore)

    # 3. committente: striscia verticale sul bordo sinistro, corpo minimo
    dr.rectangle((int(W * 0.016), int(H * 0.10), int(W * 0.034), int(H * 0.42)),
                 fill=BLOCCO)
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
