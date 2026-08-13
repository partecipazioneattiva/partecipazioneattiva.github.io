#!/usr/bin/env python3
"""Misura lo SPAZIO VUOTO lasciato nel manifesto e scrive il comando che lo riempie.

    python3 _tools/misura_vuoto.py --manifesto manifesto_vuoto.png

⛔ PERCHE' ESISTE (4 agosto 2026, idea di Fernando)
Il manifesto si fa generare con il posto del simbolo GIA' VUOTO: un disco di solo
fondo, senza niente dentro. Cosi' il generatore non ridisegna mai il logo — non
sa nemmeno che ci andra' un logo — e il simbolo VERO si incolla dopo con
_tools/sostituisci_simbolo.py --senza-toppa.

Ma quel disco non esce mai due volte nello stesso posto: le frazioni --x --y
--lato vanno RIMISURATE a ogni generazione, o il logo finisce di traverso.
Misurarle a occhio costa tempo e sbaglia. Qui si misurano da sole.

COME LO TROVA
Il disco vuoto e' l'unica zona larga di colore piatto: si parte da un punto
interno e si allarga per diffusione finche' il colore cambia (flood fill), poi
si prende il rettangolo che contiene la macchia. Il punto interno lo si cerca
da solo nella meta' bassa a sinistra — l'angolo dove i nostri manifesti mettono
il simbolo — scegliendo la macchia piatta piu' grande. Con --punto x,y si
indica a mano quando il manifesto ha il vuoto altrove.

LA PROVA CHE E' IL DISCO GIUSTO
area / (pi * r^2) deve stare vicino a 1: un rettangolo darebbe 1,27 e una
macchia sbavata sul fondo darebbe molto di piu'. Sotto 0,90 o sopra 1,10 lo
script avvisa e NON scrive il comando: quasi sempre vuol dire che il colore del
disco e quello del fondo sono troppo simili e la diffusione e' colata fuori.
"""
import argparse


import numpy as np
from PIL import Image

# Tolleranza di colore della diffusione, come somma delle differenze RGB.
# 14 tiene insieme la sfumatura interna del disco senza scavalcare il bordo:
# sul manifesto di Luigi disco e fondo distavano 22 (F3E6C3 contro F2E0B5).
TOLLERANZA = 14


def macchia(a, sx, sy, tol=TOLLERANZA):
    """Rettangolo e area della macchia di colore piatto che contiene (sx, sy).

    Diffusione a righe intere, non a pixel: si allarga la riga finche' il colore
    tiene, poi si accodano solo le righe sopra e sotto. Su un disco da centomila
    pixel sono qualche centinaio di passi invece di centomila.
    """
    H, W, _ = a.shape
    seme = a[sy, sx].copy()
    simile = np.abs(a - seme).sum(axis=2) < tol   # una volta sola, vettoriale
    visti = np.zeros((H, W), bool)
    pila = [(sx, sy)]
    x0 = x1 = sx
    y0 = y1 = sy
    n = 0
    while pila:
        x, y = pila.pop()
        if visti[y, x] or not simile[y, x]:
            continue
        riga = simile[y]
        sin = x
        while sin > 0 and riga[sin - 1] and not visti[y, sin - 1]:
            sin -= 1
        des = x
        while des < W - 1 and riga[des + 1] and not visti[y, des + 1]:
            des += 1
        visti[y, sin:des + 1] = True
        n += des - sin + 1
        x0, x1 = min(x0, sin), max(x1, des)
        y0, y1 = min(y0, y), max(y1, y)
        for vicina in (y - 1, y + 1):
            if 0 <= vicina < H:
                fascia = simile[vicina, sin:des + 1] & ~visti[vicina, sin:des + 1]
                # un solo punto per ogni tratto contiguo della riga vicina
                bordi = np.flatnonzero(fascia & ~np.r_[False, fascia[:-1]])
                pila.extend((sin + int(b), vicina) for b in bordi)
    return x0, x1, y0, y1, n


def cerca_punto(a):
    """Il punto interno alla macchia piatta piu' grande, in basso a sinistra."""
    H, W, _ = a.shape
    migliore = None
    # Griglia larga: bastano pochi assaggi per trovare un disco grande, e ogni
    # assaggio costa una diffusione intera.
    for y in range(int(H * 0.55), int(H * 0.98), 24):
        for x in range(int(W * 0.02), int(W * 0.55), 24):
            r = macchia(a, x, y)
            larg = r[1] - r[0] + 1
            alt = r[3] - r[2] + 1
            # Un disco: largo almeno un decimo della tela e grosso modo tondo.
            if larg < W * 0.10 or not 0.75 < larg / alt < 1.33:
                continue
            if migliore is None or r[4] > migliore[0][4]:
                migliore = (r, x, y)
    return migliore


def main():
    p = argparse.ArgumentParser(description="Misura il vuoto del manifesto")
    p.add_argument("--manifesto", required=True)
    p.add_argument("--punto", help="x,y dentro il vuoto, se non lo trova da solo")
    p.add_argument("--logo", default="~/Desktop/Claude IA/04_MANIFESTI_E_CARD/GEMINI LAVORI/<Nome>/logo_pa.png")
    p.add_argument("--uscita", default="manifesto_finale.png")
    p.add_argument("--carta", default="70x100",
                   help="misura del foglio in cm, per la conversione")
    a_ = p.parse_args()

    im = Image.open(a_.manifesto).convert("RGB")
    a = np.array(im).astype(int)
    H, W, _ = a.shape

    if a_.punto:
        sx, sy = (int(v) for v in a_.punto.split(","))
        r, sx, sy = macchia(a, sx, sy), sx, sy
    else:
        trovato = cerca_punto(a)
        if trovato is None:
            print("❌ nessun vuoto tondo trovato: indicane uno con --punto x,y")
            return 1
        r, sx, sy = trovato

    x0, x1, y0, y1, n = r
    larg, alt = x1 - x0 + 1, y1 - y0 + 1
    raggio = (larg + alt) / 4
    rotondita = n / (np.pi * raggio ** 2)

    cm_l, cm_h = (float(v) for v in a_.carta.lower().split("x"))
    print(f"manifesto: {W} × {H} px  ·  carta {cm_l:g} × {cm_h:g} cm")
    colore = "#%02X%02X%02X" % tuple(int(v) for v in a[sy, sx])
    print(f"vuoto trovato dal punto ({sx}, {sy}), colore {colore}")
    print(f"  bordo sinistro {x0} px   = {x0/W:.3f} larg  = {x0/W*cm_l:.1f} cm")
    print(f"  bordo alto     {y0} px   = {y0/H:.3f} alt   = {y0/H*cm_h:.1f} cm")
    print(f"  diametro       {larg} px = {larg/W:.3f} larg = {larg/W*cm_l:.1f} cm"
          f"   (altezza {alt} px)")
    print(f"  centro         ({(x0+x1)//2}, {(y0+y1)//2}) px")
    print(f"  rotondita'     {rotondita:.3f}  (1,000 = disco perfetto)")

    if not 0.90 < rotondita < 1.10:
        print("\n⚠️  NON e' un disco pulito: la diffusione e' probabilmente colata")
        print("    sul fondo, oppure il vuoto e' rettangolare. Il comando non si")
        print("    scrive: guarda l'immagine e indica il punto giusto con --punto.")
        return 1

    # ⭐ IL SIMBOLO SI INCOLLA UN FILO PIU' GRANDE DEL VUOTO (Fernando, 4 agosto
    #    2026). Il disco e' di una tinta appena diversa dal fondo: se il simbolo
    #    lo copre al pixel esatto va bene, ma basta sbagliare di un capello e
    #    resta un anello chiaro tutto intorno. Allargandolo dell'1,5% il vuoto
    #    finisce sempre sotto, e il simbolo — che e' tondo e pieno — sborda sulla
    #    giacca senza che si veda.
    cresci = 1.015
    lato = larg / W * cresci
    cx, cy = (x0 + x1) / 2 / W, (y0 + y1) / 2 / H
    nx = cx - lato / 2
    ny = cy - lato * W / H / 2      # il diametro e' in frazioni di LARGHEZZA
    print(f"\nda incollare (simbolo allargato dell'1,5%, cosi' il vuoto ci sta"
          f" sempre sotto):\n")
    print(f"python3 _tools/sostituisci_simbolo.py \\\n"
          f"    --manifesto {a_.manifesto!r} \\\n"
          f"    --logo {a_.logo!r} \\\n"
          f"    --uscita {a_.uscita!r} \\\n"
          f"    --senza-toppa --x {nx:.3f} --y {ny:.3f} --lato {lato:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
