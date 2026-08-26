#!/usr/bin/env python3
"""Esclude navbar/footer/topbar/menu/modali dall'indice di ricerca.

NON si usa data-pagefind-body come da incarico: se anche UNA pagina ce l'ha,
Pagefind indicizza SOLO le pagine che ce l'hanno. Qui 'article-wrap' esiste
su 41 pagine su 65 -> home, battaglie, webtv, proposte sparirebbero.

I modali hanno markup diverso per eta' della pagina (modal-sostienici,
modal-sost, class=modal-overlay): il selettore li prende tutti.

    python3 _tools/pagefind_ignora.py [--applica]
"""
import glob
import re
import shutil
import sys
from datetime import datetime

BASE = '/Users/osxssd/Desktop/ARCHIVIO GENERALE/LAVORI/partecipazioneattiva/'
SALTA = {'template.html'}

# (etichetta, regex sul tag di apertura). Il gruppo 1 e' il tag da marcare.
BERSAGLI = [
    ('navbar',   r'<nav\b(?![^>]*data-pagefind-ignore)'),
    ('footer',   r'<footer\b(?![^>]*data-pagefind-ignore)'),
    ('topbar',   r'<div\b(?=[^>]*class=["\']?topbar\b)(?![^>]*data-pagefind-ignore)'),
    ('menu mob', r'<div\b(?=[^>]*(?:class=["\']?mob-menu\b|id=["\']?mobmenu\b))(?![^>]*data-pagefind-ignore)'),
    # I modali hanno markup diverso a seconda dell'eta' della pagina:
    # id=modal-sostienici, id=modal-sost, class="modal-overlay". Li prendo tutti:
    # un modale non e' mai contenuto da cercare.
    ('modale',   r'<div\b(?=[^>]*(?:id=["\']?modal|class=["\'][^"\']*\bmodal))(?![^>]*data-pagefind-ignore)'),
    ('ticker',   r'<div\b(?=[^>]*data-pa-section=["\']?ticker\b)(?![^>]*data-pagefind-ignore)'),
]


def main():
    applica = '--applica' in sys.argv
    marca = datetime.now().strftime('%Y%m%d_%H%M%S')
    totali = {e: 0 for e, _ in BERSAGLI}
    toccate = 0

    for path in sorted(glob.glob(BASE + '*.html')):
        f = path.rsplit('/', 1)[1]
        if f in SALTA or f.startswith('google'):
            continue
        orig = open(path, encoding='utf-8').read()
        s = orig
        for etichetta, pat in BERSAGLI:
            s, k = re.subn(pat, lambda m: m.group(0) + ' data-pagefind-ignore', s)
            totali[etichetta] += k
        if s != orig:
            toccate += 1
            if applica:
                shutil.copy(path, f'/tmp/{f}.{marca}.bak')
                open(path, 'w', encoding='utf-8').write(s)

    print(f'pagine modificate: {toccate}')
    for etichetta, _ in BERSAGLI:
        print(f'   {etichetta:10} {totali[etichetta]:3d} occorrenze escluse')
    if not applica:
        print('\nANTEPRIMA. Rilancia con --applica per scrivere.')


if __name__ == '__main__':
    main()
