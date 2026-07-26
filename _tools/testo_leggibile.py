#!/usr/bin/env python3
"""Toglie la dimensione rimpicciolita scritta dentro i paragrafi di testo lungo.

MISURATO il 26/07/2026: i paragrafi degli articoli venivano a 14,7 px invece
dei 16-17 comodi per un testo lungo. La causa non era il foglio di stile: era
che ogni paragrafo si porta dentro un attributo style="font-size:.92em", e un
attributo scritto sul tag batte qualsiasi foglio di stile.

Si toglie la dimensione SOLO dai <p> che contengono testo lungo (oltre 120
caratteri): quelli sono testo da leggere. Etichette, didascalie, bottoni e
badge restano come sono — devono essere piccoli, e sono la maggioranza degli
840 attributi presenti nel sito.

Tolta la dimensione dal tag, comanda css/pa-leggibilita.css: 1,05rem.

    python3 _tools/testo_leggibile.py            # mostra cosa cambierebbe
    python3 _tools/testo_leggibile.py --applica  # scrive
"""
import glob
import os
import re
import sys

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
MIN_CARATTERI = 120
PARAGRAFO = re.compile(r'<p([^>]*\bstyle="[^"]*")([^>]*)>(.*?)</p>', re.S | re.I)
DIMENSIONE = re.compile(r'font-size:\s*([\d.]+)(em|rem|px)\s*;?', re.I)


def piccola(valore, unita):
    v = float(valore)
    return (unita.lower() in ('em', 'rem') and v < 1) or (unita.lower() == 'px' and v < 16)


def main():
    applica = '--applica' in sys.argv
    cambiati, saltati_corti, pagine = 0, 0, 0

    for perc in sorted(glob.glob(BASE + '*.html')):
        s = open(perc, encoding='utf-8').read()
        conta = [0, 0]

        def sost(m):
            attr, resto, dentro = m.group(1), m.group(2), m.group(3)
            testo = re.sub(r'<[^>]+>', '', dentro).strip()
            d = DIMENSIONE.search(attr)
            if not d or not piccola(d.group(1), d.group(2)):
                return m.group(0)
            if len(testo) < MIN_CARATTERI:
                conta[1] += 1
                return m.group(0)
            conta[0] += 1
            nuovo = DIMENSIONE.sub('', attr)
            nuovo = re.sub(r'style="\s*;*\s*"', '', nuovo)   # se resta vuoto, via
            return f'<p{nuovo}{resto}>{dentro}</p>'

        nuovo_testo = PARAGRAFO.sub(sost, s)
        if conta[0]:
            pagine += 1
            cambiati += conta[0]
            if applica:
                open(perc, 'w', encoding='utf-8').write(nuovo_testo)
        saltati_corti += conta[1]

    print(f'paragrafi di testo lungo riportati alla dimensione normale: {cambiati} '
          f'su {pagine} pagine')
    print(f'paragrafi corti lasciati com\'erano (didascalie, etichette): {saltati_corti}')
    if not applica:
        print('\n(prova a vuoto: rilancia con --applica)')


if __name__ == '__main__':
    main()
