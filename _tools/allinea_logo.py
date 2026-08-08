#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IL LOGO CON LE SCRITTE — IDENTICO SU TUTTI I MENU, NESSUNO ESCLUSO
==================================================================
Ordine di Fernando, 8 agosto 2026:
  «questo e' il logo con le scritte da applicare a tutte le pagine, puoi
   adattare la grandezza ma deve essere ESATTAMENTE uguale, e deve essere in
   tutti i menu nessuno escluso. Nessuna iniziativa di modificarlo, tolta la
   dimensione se serve.»

IL BLOCCO, esattamente come nel disegno che ha mandato:

    (logo tondo)   Partecipazione
                   Attiva
                   MOVIMENTO
                   POPOLARE DEI
                   CITTADINI ITALIANI

⚠️ LE INTERRUZIONI DI RIGA SONO FISSE (<br>), NON AFFIDATE AL BROWSER.
Motivo misurato: "MOVIMENTO POPOLARE" e' lungo quanto "CITTADINI ITALIANI",
quindi lasciando andare a capo il browser il testo si spezzerebbe come
"MOVIMENTO POPOLARE / DEI CITTADINI / ITALIANI" — non come nel disegno.
Con le interruzioni fisse il blocco e' identico su ogni pagina e a ogni
larghezza di schermo.

L'aspetto (carattere, corpo, colori, spaziatura) sta in css/pa-intestazione.css.
Qui c'e' solo il testo e la struttura.

    python3 _tools/allinea_logo.py            # prova a vuoto
    python3 _tools/allinea_logo.py --applica
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv

NOME = "Partecipazione<br>Attiva"
SOTTO = "MOVIMENTO<br>POPOLARE DEI<br>CITTADINI ITALIANI"

BUONO = ('<img src="LOGO-PA.webp" alt="Partecipazione Attiva — Movimento Popolare '
         'dei Cittadini Italiani" width="68" height="68">'
         f'<div class="nav-nome">{NOME}<small>{SOTTO}</small></div>')

# prende il blocco logo qualunque forma abbia oggi
RE_BLOCCO = re.compile(
    r'(<a[^>]*class="?nav-logo"?[^>]*>|<div[^>]*class="?nav-logo"?[^>]*>)\s*'
    r'<img[^>]*>\s*'
    r'<div class="?nav-nome"?>(.*?)</div>\s*'
    r'(</a>|</div>)',
    re.S)


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto (non scrivo niente)")
    cambiate = gia = senza = 0
    for f in sorted(x for x in os.listdir(REPO) if x.endswith(".html")):
        p = os.path.join(REPO, f)
        d = open(p, encoding="utf-8").read()
        m = RE_BLOCCO.search(d)
        if not m:
            if "<nav" in d:
                senza += 1
                print(f"  ⚠️  {f}: ha un menu ma non riconosco il blocco del logo")
            continue
        nuovo = m.group(1) + BUONO + m.group(3)
        if m.group(0) == nuovo:
            gia += 1
            continue
        cambiate += 1
        print(f"  ✏️  {f}")
        if APPLICA:
            open(p, "w", encoding="utf-8").write(d[:m.start()] + nuovo + d[m.end():])
    print(f"\n  {cambiate} pagine aggiornate · {gia} gia' identiche · {senza} da guardare a mano")
    if not APPLICA:
        print("  (rilancia con --applica per scrivere)")


if __name__ == "__main__":
    main()
