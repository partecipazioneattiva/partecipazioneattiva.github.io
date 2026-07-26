#!/usr/bin/env python3
"""Toglie dalle pagine il CSS identico ripetuto e lo mette in un file solo.

PERCHE' (misurato il 26/07/2026, rapporto in _audit/): le 65 pagine si
portavano dentro 430 KB di CSS IDENTICO, ripetuto pagina per pagina. Due
conseguenze, la seconda peggiore della prima:

1. ogni visitatore riscarica lo stesso stile a ogni pagina che apre;
2. ogni difetto di grafica va corretto 65 volte. I contrasti fuori norma e il
   testo troppo piccolo stavano tutti li' dentro.

Con un file esterno il browser lo scarica UNA volta e lo tiene, e da li' in poi
una correzione si fa in un posto solo.

COME, senza rischiare la grafica: si estraggono solo i blocchi <style> che sono
IDENTICI carattere per carattere su molte pagine, e il collegamento al file
esterno si mette ESATTAMENTE dove stava il blocco. L'ordine di lettura del CSS
non cambia, quindi non cambia quale regola vince.

    python3 _tools/estrai_css.py            # mostra cosa farebbe
    python3 _tools/estrai_css.py --applica  # scrive css/ e riscrive le pagine
"""
import collections
import glob
import hashlib
import os
import re
import sys

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
CARTELLA = BASE + 'css/'
SOGLIA_PAGINE = 10      # sotto questa diffusione non vale la pena estrarre
# Un blocco piccolo NON va estratto: una richiesta in piu' al server costa piu'
# dei byte che risparmia. Misurato: un blocco da 0,1 KB su 54 pagine "risparmia"
# 4 KB in tutto, e in cambio aggiunge un file da scaricare a ogni pagina.
SOGLIA_BYTE = 1000

# Nomi dati ai blocchi riconosciuti, in base a cosa contengono.
NOMI = [
    (r'\.article-hero|\.topbar', 'pa-base.css'),
    (r'\.pa-cerca-btn', 'pa-ricerca.css'),
]
STILE = re.compile(r'<style[^>]*>(.*?)</style>', re.S)


def nome_per(testo, n):
    for pat, nome in NOMI:
        if re.search(pat, testo):
            return nome
    return f'pa-comune-{n}.css'


def main():
    applica = '--applica' in sys.argv
    pagine = sorted(glob.glob(BASE + '*.html'))
    conta = collections.Counter()
    testo_di = {}
    for p in pagine:
        for x in STILE.findall(open(p, encoding='utf-8').read()):
            h = hashlib.sha256(x.encode()).hexdigest()[:10]
            conta[h] += 1
            testo_di[h] = x

    da_estrarre = {h: nome_per(testo_di[h], i)
                   for i, (h, c) in enumerate(conta.most_common())
                   if c >= SOGLIA_PAGINE and len(testo_di[h]) >= SOGLIA_BYTE}
    if not da_estrarre:
        print('nessun blocco abbastanza diffuso: niente da fare')
        return

    for h, nome in da_estrarre.items():
        print(f'{nome:16s} {len(testo_di[h])/1024:5.1f} KB  su {conta[h]:2d} pagine  '
              f'-> {(conta[h]-1)*len(testo_di[h])/1024:6.0f} KB di duplicazione tolti')

    if not applica:
        print('\n(prova a vuoto: rilancia con --applica)')
        return

    os.makedirs(CARTELLA, exist_ok=True)
    for h, nome in da_estrarre.items():
        intestazione = (f'/* Stile comune a {conta[h]} pagine. Stava copiato dentro '
                        f'ognuna di esse.\n   Lo estrae _tools/estrai_css.py — '
                        f'le modifiche si fanno QUI, non nelle pagine. */\n')
        open(CARTELLA + nome, 'w', encoding='utf-8').write(intestazione + testo_di[h])

    toccate, tolti = 0, 0
    for p in pagine:
        s = originale = open(p, encoding='utf-8').read()

        def sost(m):
            h = hashlib.sha256(m.group(1).encode()).hexdigest()[:10]
            if h not in da_estrarre:
                return m.group(0)
            return f'<link rel="stylesheet" href="css/{da_estrarre[h]}">'
        s = STILE.sub(sost, s)
        if s != originale:
            open(p, 'w', encoding='utf-8').write(s)
            toccate += 1
            tolti += len(originale) - len(s)
    print(f'\npagine riscritte: {toccate}   HTML tolto: {tolti/1024:.0f} KB')


if __name__ == '__main__':
    main()
