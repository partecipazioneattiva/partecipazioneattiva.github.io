#!/usr/bin/env python3
"""Toglie lo sbordamento orizzontale della navbar su mobile.

Misurato il 26/07/2026 su iPhone (375px): la pagina era larga 557px, si
trascinava di lato. Causa: nel CSS ci sono tre regole in conflitto e le
ultime due vincono, quindi .nav-cta non si nasconde MAI.

    @media (max-width:900px) { .nav-cta: none }   <- corretta
    @media (min-width:701px) { .nav-cta: flex }   <- la annulla
    @media (max-width:700px) { .nav-cta: flex }   <- pure

Non si nascondono i pulsanti: "Iscriviti" e "Sostienici" NON sono nel menu
hamburger, nasconderli toglierebbe la chiamata all'azione principale da
mobile. Si manda a capo la navbar: nulla sparisce, lo sbordamento va a zero.

    python3 _tools/fix_navbar_mobile.py [--applica]
"""
import glob
import re
import shutil
import sys
from datetime import datetime

BASE = '/Users/osxssd/Desktop/ARCHIVIO GENERALE/LAVORI/partecipazioneattiva/'

BLOCCO = ('<!--PA-NAVFIX--><style>@media(max-width:900px){'
          '.navbar{flex-wrap:wrap}.nav-cta{margin-left:0}}'
          '</style><!--/PA-NAVFIX-->')


def main():
    applica = '--applica' in sys.argv
    marca = datetime.now().strftime('%Y%m%d_%H%M%S')
    fatte, senza = [], []

    for path in sorted(glob.glob(BASE + '*.html')):
        f = path.rsplit('/', 1)[1]
        if f.startswith('google'):
            continue
        orig = open(path, encoding='utf-8').read()
        if 'nav-cta' not in orig:
            senza.append(f)
            continue
        s = re.sub(r'<!--PA-NAVFIX-->.*?<!--/PA-NAVFIX-->', '', orig, flags=re.S)
        i = s.rfind('</body>')
        if i < 0:
            senza.append(f + ' (niente </body>)')
            continue
        s = s[:i] + BLOCCO + s[i:]
        if s != orig:
            if applica:
                shutil.copy(path, f'/tmp/{f}.{marca}.bak')
                open(path, 'w', encoding='utf-8').write(s)
            fatte.append(f)

    print(f'pagine corrette: {len(fatte)}')
    if senza:
        print(f'pagine senza .nav-cta (nessuna correzione serve): {len(senza)}')
    if not applica:
        print('\nANTEPRIMA. Rilancia con --applica per scrivere.')


if __name__ == '__main__':
    main()
