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

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

# Soglia in caratteri sotto la quale un <p> si considera didascalia e non si
# tocca. 120 era la scelta del 26/07/2026. Il 19/08/2026 ho misurato che le
# descrizioni delle schede in home stanno fra 60 e 160 caratteri: la meta'
# restava fuori, ferma a 12,6-13,1 px, sotto il minimo di 16 px indicato per
# la lettura su telefono — dove arriva il 68% di chi ci legge.
# Si abbassa con --minimo N, e si guarda SEMPRE la prova a vuoto prima.
MIN_CARATTERI = 120
# ⚠️ L'HTML di questo sito e' minificato e meta' degli attributi NON hanno le
# virgolette: <p style=font-size:.85rem;color:#666;margin:0>. La prima versione
# di questo strumento cercava solo style="..." e il 19/08/2026 si e' scoperto
# che saltava cinque paragrafi su index.html senza dirlo. Ora legge le tre
# forme: doppie virgolette, singole, e nessuna (che finisce al primo spazio).
PARAGRAFO = re.compile(r'<p\b([^>]*)>(.*?)</p>', re.S | re.I)
STILE = re.compile(r'\bstyle=(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))', re.I)
DIMENSIONE = re.compile(r'font-size:\s*([\d.]+)(em|rem|px)\s*;?', re.I)


def piccola(valore, unita):
    v = float(valore)
    return (unita.lower() in ('em', 'rem') and v < 1) or (unita.lower() == 'px' and v < 16)


def soglia():
    if '--minimo' in sys.argv:
        return int(sys.argv[sys.argv.index('--minimo') + 1])
    return MIN_CARATTERI


def main():
    applica = '--applica' in sys.argv
    minimo = soglia()
    cambiati, saltati_corti, pagine = 0, 0, 0
    elenco = []

    for perc in sorted(glob.glob(BASE + '*.html')):
        s = open(perc, encoding='utf-8').read()
        conta = [0, 0]

        def sost(m):
            attr, dentro = m.group(1), m.group(2)
            testo = re.sub(r'<[^>]+>', '', dentro).strip()
            s = STILE.search(attr)
            if not s:
                return m.group(0)
            valore = s.group(1) or s.group(2) or s.group(3) or ''
            d = DIMENSIONE.search(valore)
            if not d or not piccola(d.group(1), d.group(2)):
                return m.group(0)
            if len(testo) < minimo:
                conta[1] += 1
                return m.group(0)
            conta[0] += 1
            elenco.append((os.path.basename(perc), d.group(1) + d.group(2), testo[:58]))
            ripulito = DIMENSIONE.sub('', valore).strip().strip(';').strip()
            # riscritto sempre con le virgolette: e' HTML piu' corretto, e un
            # valore senza virgolette si spezza al primo spazio.
            sostituto = '' if not ripulito else 'style="%s"' % ripulito
            attr_nuovo = attr[:s.start()] + sostituto + attr[s.end():]
            attr_nuovo = re.sub(r'\s{2,}', ' ', attr_nuovo).rstrip()
            return '<p%s>%s</p>' % (attr_nuovo, dentro)

        nuovo_testo = PARAGRAFO.sub(sost, s)
        if conta[0]:
            pagine += 1
            cambiati += conta[0]
            if applica:
                open(perc, 'w', encoding='utf-8').write(nuovo_testo)
        saltati_corti += conta[1]

    if not applica:
        for pag, dim, testo in elenco[:40]:
            print('  %-46s %-6s %s' % (pag, dim, testo))
        if len(elenco) > 40:
            print('  ... e altri %d' % (len(elenco) - 40))
    print(f'\nsoglia usata: {minimo} caratteri')
    print(f'paragrafi di testo lungo riportati alla dimensione normale: {cambiati} '
          f'su {pagine} pagine')
    print(f'paragrafi corti lasciati com\'erano (didascalie, etichette): {saltati_corti}')
    if not applica:
        print('\n(prova a vuoto: rilancia con --applica)')


if __name__ == '__main__':
    main()
