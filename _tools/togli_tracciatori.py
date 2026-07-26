#!/usr/bin/env python3
"""Toglie dalle pagine i tracciatori di terze parti.

PERCHE' (misurato il 26/07/2026, rapporto in _audit/):
la home contattava 9 domini di terzi prima che il visitatore facesse qualcosa,
mentre l'informativa pubblicata dichiara che il sito "non utilizza cookie propri
per il tracciamento o la profilazione". Invece di riscrivere l'informativa per
giustificare i tracciatori, si rende vera l'informativa.

COSA TOGLIE:
- Google Analytics / Tag Manager (gtag, G-C0VVYWW9EM): statistiche di visita.
- Microsoft Clarity: REGISTRA LA SESSIONE del visitatore (clic, scorrimento,
  movimenti del mouse) e la ripropone come un filmato. Su un sito di un
  movimento politico e' la voce piu' pesante.

COSA NON TOCCA:
- Webpushr (notifiche push): il visitatore le accetta esplicitamente dal
  browser, ed e' un canale che il movimento usa davvero. Va dichiarato
  nell'informativa.
- Google Fonts: va ospitato sul sito (i caratteri vanno scaricati una volta),
  ed e' un intervento a parte.

    python3 _tools/togli_tracciatori.py            # mostra cosa toglierebbe
    python3 _tools/togli_tracciatori.py --applica  # riscrive le pagine
"""
import glob
import os
import re
import sys

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'

TRACCIATORI = [
    # Fra i due <script> ci puo' essere dell'a capo o dell'indentazione: le
    # pagine sono state scritte in momenti diversi. Senza \s* il blocco
    # combaciava su 10 pagine su 51, e si sarebbero tolte le chiamate lasciando
    # lo script che le carica.
    ('Google Analytics',
     re.compile(r'<script async src="https://www\.googletagmanager\.com/gtag/js\?'
                r'id=[^"]+"></script>\s*<script>\s*window\.dataLayer.*?</script>', re.S)),
    ('Microsoft Clarity',
     re.compile(r'<script>\(function\(e,t,n,s,o,i,a\)\{[^<]*?clarity[^<]*?</script>', re.S)),
]

# Resti che possono restare in giro se una pagina e' stata scritta a mano.
RESIDUI = [
    ('chiamata gtag() isolata', re.compile(r'\s*gtag\((?:[^()]|\([^()]*\))*\);?')),
    ('preconnect a googletagmanager',
     re.compile(r'<link[^>]+href=["\']?https://www\.googletagmanager\.com[^>]*>')),
    ('preconnect a clarity',
     re.compile(r'<link[^>]+href=["\']?https://[a-z.]*clarity\.ms[^>]*>')),
]


def main():
    applica = '--applica' in sys.argv
    conta = {n: 0 for n, _ in TRACCIATORI + RESIDUI}
    toccate, byte_tolti = [], 0

    for perc in sorted(glob.glob(BASE + '*.html')):
        s = originale = open(perc, encoding='utf-8').read()
        for nome, pat in TRACCIATORI + RESIDUI:
            s, n = pat.subn('', s)
            conta[nome] += n
        if s != originale:
            toccate.append(os.path.basename(perc))
            byte_tolti += len(originale) - len(s)
            if applica:
                open(perc, 'w', encoding='utf-8').write(s)

    for nome, n in conta.items():
        print(f'{nome:32s} {n:3d} rimozioni')
    print(f'\npagine toccate: {len(toccate)}   byte tolti: {byte_tolti/1024:.1f} KB')

    # Controllo di sicurezza: nessun riferimento deve sopravvivere.
    if applica:
        resta = []
        for perc in glob.glob(BASE + '*.html'):
            s = open(perc, encoding='utf-8').read()
            for spia in ('clarity.ms', 'googletagmanager', 'gtag(', 'dataLayer'):
                if spia in s:
                    resta.append(f'{os.path.basename(perc)}: {spia}')
        print('VERIFICA: ' + ('nessun residuo, pulizia completa' if not resta
                              else f'ATTENZIONE, restano {len(resta)}: {resta[:5]}'))
    else:
        print('\n(prova a vuoto: rilancia con --applica per riscrivere le pagine)')


if __name__ == '__main__':
    main()
