#!/usr/bin/env python3
"""Scrive larghezza e altezza vere dentro ogni tag <img>.

PERCHE': senza width e height il browser non sa quanto spazio riservare a
un'immagine finche' non l'ha scaricata. Quando arriva, il testo gia' scritto
viene spinto piu' giu': la pagina SALTA mentre carica, e chi sta leggendo
perde la riga. Su un sito letto da persone anziane e' fastidio puro.

Misurato il 26/07/2026: solo 21 tag <img> su 245 dichiaravano le dimensioni.

Le dimensioni si leggono dal file vero, non si inventano. Il CSS continua a
comandare la resa (le immagini restano fluide): width e height servono solo a
dire al browser le PROPORZIONI, cosi' riserva il posto giusto.

    python3 _tools/dimensioni_immagini.py            # mostra
    python3 _tools/dimensioni_immagini.py --applica  # scrive
"""
import glob
import os
import re
import sys

from PIL import Image

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
TAG = re.compile(r'<img\b([^>]*)>', re.I)
SRC = re.compile(r'\bsrc=["\']?([^"\'\s>]+)', re.I)

misure = {}


def dimensione(src):
    perc = BASE + src.split('?')[0].lstrip('/')
    if src.startswith(('http://', 'https://', 'data:')) or not os.path.exists(perc):
        return None
    if perc not in misure:
        try:
            with Image.open(perc) as im:
                misure[perc] = im.size
        except Exception:
            misure[perc] = None
    return misure[perc]


def main():
    applica = '--applica' in sys.argv
    aggiunte, gia, esterne, mancanti = 0, 0, 0, []

    for pagina in sorted(glob.glob(BASE + '*.html')):
        s = open(pagina, encoding='utf-8').read()
        cambi = [0]

        def sost(m):
            global aggiunte
            attr = m.group(1)
            if re.search(r'\bwidth=', attr, re.I) and re.search(r'\bheight=', attr, re.I):
                return m.group(0)
            src = SRC.search(attr)
            if not src:
                return m.group(0)
            d = dimensione(src.group(1))
            if not d:
                return m.group(0)
            cambi[0] += 1
            # in coda agli attributi, senza toccare quelli che c'erano
            return f'<img{attr.rstrip()} width="{d[0]}" height="{d[1]}">'

        nuovo = TAG.sub(sost, s)
        aggiunte += cambi[0]
        if cambi[0] and applica:
            open(pagina, 'w', encoding='utf-8').write(nuovo)

    # riepilogo dello stato
    tot = con = 0
    for pagina in glob.glob(BASE + '*.html'):
        for m in TAG.finditer(open(pagina, encoding='utf-8').read()):
            tot += 1
            if re.search(r'\bwidth=', m.group(1), re.I):
                con += 1
            else:
                src = SRC.search(m.group(1))
                if src and src.group(1).startswith(('http', 'data:')):
                    esterne += 1
                elif src:
                    mancanti.append(src.group(1))   # locali ancora senza misura

    print(f'tag <img> nel sito: {tot}')
    print(f'  dimensioni {"scritte ora" if applica else "da scrivere"}: {aggiunte}')
    print(f'  ora ne hanno: {con}/{tot}')
    print(f'  immagini remote (non misurabili): {esterne}')
    if mancanti:
        print(f'  locali ancora senza dimensioni: {len(mancanti)} '
              f'-> {sorted(set(mancanti))[:3]}')
    if not applica:
        print('\n(prova a vuoto: rilancia con --applica)')


if __name__ == '__main__':
    main()
