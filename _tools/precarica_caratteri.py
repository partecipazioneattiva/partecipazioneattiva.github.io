#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRECARICA I CARATTERI DELLA PRIMA SCHERMATA
===========================================
Fase 1.5 del piano esecutivo.

IL PROBLEMA, MISURATO l'8 agosto 2026: la pagina si riassestava dopo essere gia'
apparsa (CLS 0,173, di cui 0,165 dovuti da soli alla barra del menu). Chi stava
per toccare una voce ne toccava un'altra.

LA CAUSA: tutti i caratteri sono dichiarati "font-display: swap" e NESSUNO era
precaricato. Il browser disegna prima col carattere di ripiego, poi arriva
Montserrat, le lettere cambiano larghezza, il menu passa da due righe a tre e
spinge giu' tutto il resto.

LA CURA: dire al browser di scaricare SUBITO i tre caratteri che servono nella
prima schermata, invece di scoprirli dopo aver letto il foglio di stile.
Non cambia quanti byte si scaricano — quei file venivano scaricati lo stesso.
Cambia QUANDO.

Quali tre, e perche' proprio quelli (contati sulla home a 1512 px):
    montserrat 900   31 elementi nella prima schermata
    montserrat 700   22 elementi
    merriweather 700  1 elemento — ma e' il titolo grande, il piu' vistoso

    python3 _tools/precarica_caratteri.py            # prova a vuoto
    python3 _tools/precarica_caratteri.py --applica
"""
import os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv

ANCORA = '<link href="fonts/caratteri.css" rel="stylesheet">'

# crossorigin e' OBBLIGATORIO sui caratteri: senza, il browser li scarica DUE
# volte (una per il preload e una per l'uso) e il rimedio diventa un danno.
PRELOAD = (
    '<link rel=preload as=font type=font/woff2 crossorigin '
    'href=fonts/montserrat-900-latin.woff2>'
    '<link rel=preload as=font type=font/woff2 crossorigin '
    'href=fonts/montserrat-700-latin.woff2>'
    '<link rel=preload as=font type=font/woff2 crossorigin '
    'href=fonts/merriweather-700-latin.woff2>'
)


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto")
    fatte = saltate = senza = 0
    for f in sorted(x for x in os.listdir(REPO) if x.endswith(".html")):
        p = os.path.join(REPO, f)
        d = open(p, encoding="utf-8").read()
        if "montserrat-900-latin.woff2" in d and "rel=preload as=font" in d:
            saltate += 1
            continue
        if ANCORA not in d:
            senza += 1
            print(f"  ⚠️  {f}: non trovo il richiamo a caratteri.css, salto")
            continue
        nuovo = d.replace(ANCORA, PRELOAD + ANCORA, 1)
        fatte += 1
        if APPLICA:
            open(p, "w", encoding="utf-8").write(nuovo)
    print(f"\n  {fatte} pagine aggiornate · {saltate} gia' a posto · {senza} senza ancora")
    if not APPLICA:
        print("  (rilancia con --applica per scrivere)")


if __name__ == "__main__":
    main()
