#!/usr/bin/env python3
"""ALLINEA IL MENU DI TUTTE LE PAGINE A UNA VERSIONE UNICA.

PERCHE' ESISTE:
Il sito e' HTML statico senza template condiviso: ogni pagina si porta dentro
la propria copia del menu. Risultato misurato il 26/07/2026 su 54 pagine:
10 versioni diverse, da 3 a 13 voci. "WebTV" compariva in 3 menu su 54,
"Chi Siamo" in 12 su 54. Chi arrivava su un articolo da Facebook non aveva
modo di raggiungere meta' del sito.

USO:
    cd ~/Desktop/LAVORI/partecipazioneattiva
    python3 _tools/allinea_menu.py            # anteprima
    python3 _tools/allinea_menu.py --applica  # scrive

PER AGGIUNGERE UNA VOCE IN FUTURO: modificare MENU qui sotto e rilanciare.
Una riga qui, e cambia su tutte le pagine.

NOTA: mappa.html e azioni.html avevano un'intestazione tutta loro (barra scura
compatta, 7 voci) e questo script le saltava. Dal 27/07/2026 hanno la barra
standard (_tools/allinea_barra_strumento.py) e rientrano qui come le altre.
"""
import glob
import re
import shutil
import sys
from datetime import datetime

# il menu unico del sito — l'ordine e' quello che si vede
MENU = [
    ("index.html",        "Home"),
    ("napoli.html",       "&#9679; Napoli"),
    ("territori.html",    "Territori"),
    ("mappa.html",        "Mappa"),
    ("proposte.html",     "Proposte"),
    ("azioni.html",       "Azioni"),
    ("battaglie.html",    "Battaglie"),
    ("webtv.html",        "WebTV"),
    ("rete-ape.html",     "Rete APE"),
    ("chi-siamo.html",    "Chi Siamo"),
    ("organigramma.html", "Organigramma"),
    ("parlero.html",      "Parler&ograve;"),
]

SALTA = {'template.html', '404.html',
         'conferma.html', 'cancella.html', 'contatto.html', 'esserci.html'}


def costruisci(pagina_corrente, mobile=False):
    voci = []
    for href, testo in MENU:
        attivo = ' class="active"' if href == pagina_corrente else ''
        chiudi = ' onclick="chiudi()"' if mobile else ''
        voci.append(f'<a href="{href}"{attivo}{chiudi}>{testo}</a>')
    return "".join(voci)


def main():
    applica = "--applica" in sys.argv
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    fatti, saltati = [], []

    for f in sorted(glob.glob('*.html')):
        if f in SALTA or f.startswith('google'):
            saltati.append((f, 'esclusa'))
            continue
        s = open(f, encoding='utf-8').read()

        m_desk = re.search(r'(<div class=["\']?nav-links["\']?[^>]*>)(.*?)(</div>)', s, re.S)
        if not m_desk:
            saltati.append((f, 'niente nav-links'))
            continue

        nuovo = s[:m_desk.start(2)] + costruisci(f) + s[m_desk.end(2):]

        m_mob = re.search(r'(<div class=["\']?mob-menu["\']?[^>]*>)(.*?)(</div>)', nuovo, re.S)
        n_mob = 0
        if m_mob:
            nuovo = nuovo[:m_mob.start(2)] + costruisci(f, mobile=True) + nuovo[m_mob.end(2):]
            n_mob = 1

        if nuovo != s:
            if applica:
                shutil.copy(f, f"/tmp/{f}.{marca}.bak")
                open(f, 'w', encoding='utf-8').write(nuovo)
            fatti.append((f, len(re.findall(r'href=', m_desk.group(2))), n_mob))

    print(f"menu unico: {len(MENU)} voci -> {' · '.join(t for _, t in MENU)}\n")
    print(f"pagine aggiornate: {len(fatti)}")
    for f, prima, mob in fatti:
        print(f"   {f:52} da {prima:2d} voci a {len(MENU)}" + ("  + menu mobile" if mob else ""))
    if saltati:
        print(f"\npagine saltate: {len(saltati)}")
        for f, perche in saltati:
            print(f"   {f:52} {perche}")
    if not applica:
        print("\nanteprima soltanto. Rilancia con --applica per scrivere.")


if __name__ == "__main__":
    main()
