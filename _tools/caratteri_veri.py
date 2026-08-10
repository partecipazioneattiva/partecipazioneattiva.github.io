#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
I CARATTERI DEGLI STRUMENTI ERANO TUTTI LO STESSO, E ERA IL PIU' SOTTILE
========================================================================
Estrae da ogni carattere VARIABILE in _tools/caratteri/ la versione statica del
peso scritto nel nome del file: montserrat-700-latin.ttf diventa davvero un
Montserrat da 700, non il Thin da 100.

⛔ IL DIFETTO, misurato il 10 agosto 2026
I tre file montserrat-400 / 700 / 900 disegnavano la stessa identica quantita'
di inchiostro — 1192 pixel su una riga di prova, tutti e tre. Non erano tre
pesi: era tre volte lo stesso file. Sono caratteri VARIABILI (asse wght da 100
a 900) rinominati, e un carattere variabile aperto senza istruzioni disegna il
suo peso PREDEFINITO, che per Montserrat e' 100 (Thin) e per Merriweather 300
(Light). Da qui le scritte filiformi delle anteprime social, che Fernando ha
visto e definito «quasi illeggibili».

Non c'era niente da scaricare: il peso giusto era gia' dentro il file, bastava
chiederlo. L'originale variabile resta accanto, con -variabile nel nome.

    python3 _tools/caratteri_veri.py            # dice cosa farebbe
    python3 _tools/caratteri_veri.py --applica

🟨 Riguarda SOLO i caratteri usati per disegnare le immagini. I .woff2 in
fonts/, quelli che il browser scarica per le pagine, hanno lo stesso difetto
ma vanno valutati a parte: cambiarli cambia l'aspetto di tutto il sito.
"""
import glob
import os
import re
import sys

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

CARATTERI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caratteri")
APPLICA = "--applica" in sys.argv


def peso_dal_nome(f):
    m = re.search(r"-(\d{3})-", os.path.basename(f))
    return int(m.group(1)) if m else None


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto")
    for p in sorted(glob.glob(os.path.join(CARATTERI, "*.ttf"))):
        if "-variabile" in p:
            continue
        voluto = peso_dal_nome(p)
        t = TTFont(p)
        if "fvar" not in t:
            print(f"  ✔  {os.path.basename(p):30} statico, lo lascio stare")
            continue
        asse = {a.axisTag: a for a in t["fvar"].axes}
        ora = t["OS/2"].usWeightClass
        if not voluto or "wght" not in asse:
            print(f"  ⚠️  {os.path.basename(p):30} variabile ma non so che peso chiedergli")
            continue
        voluto = min(max(voluto, int(asse['wght'].minValue)), int(asse['wght'].maxValue))
        print(f"  🔧 {os.path.basename(p):30} disegna {ora} → lo fisso a {voluto}")
        if not APPLICA:
            continue
        orig = p.replace(".ttf", "-variabile.ttf")
        if not os.path.exists(orig):
            os.rename(p, orig)
        statico = instancer.instantiateVariableFont(TTFont(orig), {"wght": voluto})
        statico["OS/2"].usWeightClass = voluto
        statico.save(p)
    if not APPLICA:
        print("\n  (rilancia con --applica per correggerli)")


if __name__ == "__main__":
    main()
