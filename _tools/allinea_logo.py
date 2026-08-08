#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALLINEA IL LOGO E IL SOTTOTITOLO DELL'INTESTAZIONE SU TUTTE LE PAGINE
=====================================================================
Scelta di Fernando, 8 agosto 2026: gli piace l'intestazione di mappa.html —
logo con accanto il nome e sotto "Movimento Popolare dei Cittadini Italiani" —
e la vuole identica su tutto il sito.

MISURATO prima di intervenire: 14 pagine su 64 non avevano il sottotitolo, e su
quelle il logo era scritto cosi':

    <img loading=lazy src="LOGO-PA.webp" width="400" height="400">

cioe' con due difetti veri, non solo estetici:
  - dichiarava 400x400 mentre si vede a 68x68: il browser riservava un buco
    enorme e poi lo rimpiccioliva, e la pagina si assestava sotto gli occhi;
  - "loading=lazy" su un'immagine che sta in cima: il browser la rimandava,
    proprio quella che si vede per prima.

    python3 _tools/allinea_logo.py            # prova a vuoto
    python3 _tools/allinea_logo.py --applica
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv

SOTTOTITOLO = "Movimento Popolare dei Cittadini Italiani"

# il blocco buono, quello di mappa.html
BUONO = ('<img src="LOGO-PA.webp" alt="Logo Partecipazione Attiva" width="68" height="68">'
         '<div class="nav-nome">Partecipazione Attiva'
         f'<small>{SOTTOTITOLO}</small></div>')

# prende il blocco logo qualunque forma abbia
RE_BLOCCO = re.compile(
    r'(<a[^>]*class="?nav-logo"?[^>]*>)\s*'      # apertura <a class=nav-logo>
    r'<img[^>]*>\s*'                              # l'immagine, comunque scritta
    r'<div class="?nav-nome"?>(.*?)</div>\s*'     # il nome (con o senza <small>)
    r'(</a>)',
    re.S)


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto")
    cambiate = gia = senza = 0
    for f in sorted(x for x in os.listdir(REPO) if x.endswith(".html")):
        p = os.path.join(REPO, f)
        d = open(p, encoding="utf-8").read()
        m = RE_BLOCCO.search(d)
        if not m:
            senza += 1
            continue
        vecchio = m.group(0)
        nuovo = m.group(1) + BUONO + m.group(3)
        if vecchio == nuovo:
            gia += 1
            continue
        note = []
        if SOTTOTITOLO not in vecchio:
            note.append("mancava il sottotitolo")
        if 'width="400"' in vecchio or "width=400" in vecchio:
            note.append("logo dichiarato 400x400")
        if "loading=lazy" in vecchio or 'loading="lazy"' in vecchio:
            note.append("logo in ritardo (lazy)")
        cambiate += 1
        print(f"  ✏️  {f:44} {' · '.join(note) if note else 'allineo'}")
        if APPLICA:
            open(p, "w", encoding="utf-8").write(d[:m.start()] + nuovo + d[m.end():])
    print(f"\n  {cambiate} pagine allineate · {gia} gia' a posto · {senza} senza intestazione")
    if not APPLICA:
        print("  (rilancia con --applica per scrivere)")


if __name__ == "__main__":
    main()
