#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNA SOLA INTESTAZIONE PER TUTTE LE PAGINE
=========================================
Ordine di Fernando, 8 agosto 2026: «devi creare il menu/navbar uguale per tutte
le pagine, le cose cambiano da dopo il menu in poi».

Fa due cose su ogni pagina:
  1. AGGANCIA il foglio comune  css/pa-intestazione.css
  2. TOGLIE dalla pagina le sue regole del menu, che altrimenti vincono sul
     foglio comune e riportano il disordine di prima.

Le regole tolte sono solo quelle che riguardano l'intestazione:
   .topbar .navbar .nav-logo .nav-nome .nav-links .nav-cta .burger .mob-menu
comprese quelle scritte dentro le @media. Tutto il resto della pagina non si
tocca: "le cose cambiano da dopo il menu in poi".

    python3 _tools/intestazione_unica.py            # prova a vuoto
    python3 _tools/intestazione_unica.py --applica

⚠️ Prima di lanciarlo con --applica: zsh ~/Desktop/SCRIPT/sistema/backup_sito.sh
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv

FOGLIO = '<link href="css/pa-intestazione.css" rel="stylesheet">'
ANCORE = ['<link href="fonts/caratteri.css" rel="stylesheet">',
          '<link href="css/pa-leggibilita.css" rel="stylesheet">',
          '<link rel="stylesheet" href="css/pa-leggibilita.css">']

CLASSI = r"topbar|navbar|nav-logo|nav-nome|nav-links|nav-cta|burger|mob-menu|btn-iscr|btn-sost"

# una regola CSS il cui selettore nomina SOLO classi dell'intestazione
RE_REGOLA = re.compile(
    r"(?<![-\w])"                       # non in mezzo a un'altra parola
    r"((?:\.(?:" + CLASSI + r")[\w.\s,:>+~()\[\]=\"'-]*?))"   # selettore
    r"\{[^{}]*\}",
    re.S)


def solo_intestazione(selettore: str) -> bool:
    """Vero se OGNI pezzo del selettore riguarda l'intestazione.
    Serve a non cancellare per sbaglio regole come '.card,.navbar'."""
    pezzi = [p.strip() for p in selettore.split(",") if p.strip()]
    if not pezzi:
        return False
    for p in pezzi:
        if not re.search(r"\.(?:" + CLASSI + r")\b", p):
            return False
    return True


def pulisci(testo: str):
    tolte = []

    def sost(m):
        sel = m.group(1).strip()
        if solo_intestazione(sel):
            tolte.append(sel[:44])
            return ""
        return m.group(0)

    nuovo = RE_REGOLA.sub(sost, testo)
    # ripulisco le @media rimaste vuote
    nuovo = re.sub(r"@media[^{]*\{\s*\}", "", nuovo)
    nuovo = re.sub(r"<style>\s*</style>", "", nuovo)
    return nuovo, tolte


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto (non scrivo niente)")
    tot_pagine = tot_regole = 0
    senza_ancora = []
    for f in sorted(x for x in os.listdir(REPO) if x.endswith(".html")):
        p = os.path.join(REPO, f)
        d = open(p, encoding="utf-8").read()
        if "<nav" not in d:
            continue
        originale = d

        # 1. aggancio il foglio comune
        if "pa-intestazione.css" not in d:
            messo = False
            for a in ANCORE:
                if a in d:
                    d = d.replace(a, a + FOGLIO, 1)
                    messo = True
                    break
            if not messo:
                senza_ancora.append(f)

        # 2. tolgo le regole locali del menu
        d, tolte = pulisci(d)

        if d != originale:
            tot_pagine += 1
            tot_regole += len(tolte)
            print(f"  ✏️  {f:46} {len(tolte):3} regole tolte")
            if APPLICA:
                open(p, "w", encoding="utf-8").write(d)

    print(f"\n  {tot_pagine} pagine · {tot_regole} regole del menu tolte")
    if senza_ancora:
        print(f"  ⚠️  senza un punto dove agganciare il foglio: {senza_ancora}")
    if not APPLICA:
        print("  (rilancia con --applica per scrivere)")


if __name__ == "__main__":
    main()
