#!/usr/bin/env python3
"""Porta a norma i contrasti dei colori del marchio, dentro CSS e pagine.

MISURATO nel browser il 26/07/2026 (linee guida WCAG, soglia 4,5:1 per il testo
normale): tutti i difetti di contrasto del sito si riducono a DUE colori.

  verde   #1a8f3c con testo bianco = 4,17:1   (bottone "Iscriviti", badge)
  arancio #e8900a con testo bianco = 2,49:1   (bottone "Sostienici", etichette)

Le due correzioni sono state scelte con il calcolo, non a occhio:

- il VERDE si scurisce del 5% -> #188739, che da' 4,60:1. A occhio e' lo stesso
  verde: e' la correzione minima che passa la soglia.
- l'ARANCIO NON si tocca: e' il colore del movimento. Si cambia il testo che ci
  sta sopra, da bianco a marrone scuro #2b1a00, che da' 6,74:1. Scurire
  l'arancio abbastanza da reggere il bianco (#a76707) l'avrebbe imbruttito.

    python3 _tools/correggi_contrasti.py            # mostra cosa cambierebbe
    python3 _tools/correggi_contrasti.py --applica  # scrive
"""
import glob
import os
import re
import sys

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
VERDE_VECCHIO, VERDE_NUOVO = '#1a8f3c', '#188739'
ARANCIO = 'e8900a'
TESTO_SU_ARANCIO = '#2b1a00'

# Un blocco di regole CSS: "selettore{dichiarazioni}"
BLOCCO = re.compile(r'([^{}]+)\{([^{}]*)\}')
BIANCO = re.compile(r'color:\s*(#fff(?:fff)?|white)\b', re.I)


def sistema_blocco(m):
    """Se il blocco dipinge di arancione e scrive in bianco, il bianco diventa
    marrone scuro. Il fondo arancione resta identico."""
    sel, dich = m.group(1), m.group(2)
    # SOLO fondo arancione pieno. I gradienti no: ".article-hero" va dal marrone
    # scuro #8a4e00 all'arancione, e su quasi tutta la sua area il bianco e'
    # perfettamente leggibile. Scurirne il testo avrebbe rovinato le testate di
    # 42 articoli per un difetto che li' non c'e'.
    ha_arancio = re.search(r'background(?:-color)?:\s*#' + ARANCIO + r'\s*[;}]', dich, re.I)
    if ha_arancio and BIANCO.search(dich):
        dich = BIANCO.sub('color:' + TESTO_SU_ARANCIO, dich)
        sistema_blocco.contati.append(sel.strip()[:44])
    return sel + '{' + dich + '}'


def lavora(testo):
    sistema_blocco.contati = []
    testo, n_verde = re.subn(VERDE_VECCHIO, VERDE_NUOVO, testo, flags=re.I)
    testo = BLOCCO.sub(sistema_blocco, testo)
    return testo, n_verde, list(sistema_blocco.contati)


def main():
    applica = '--applica' in sys.argv
    tot_verde, tot_arancio, selettori, file_toccati = 0, 0, [], 0

    for perc in sorted(glob.glob(BASE + 'css/*.css') + glob.glob(BASE + '*.html')):
        originale = open(perc, encoding='utf-8').read()
        if perc.endswith('.html'):
            # Nelle pagine si tocca solo quello che sta dentro <style>.
            pezzi = []
            fine = 0
            nuovo = originale
            n_v_tot = 0
            for m in re.finditer(r'(<style[^>]*>)(.*?)(</style>)', originale, re.S):
                corretto, n_v, sel = lavora(m.group(2))
                pezzi.append((m.start(2), m.end(2), corretto))
                n_v_tot += n_v
                selettori += sel
                tot_arancio += len(sel)
            for inizio, fine_p, corretto in reversed(pezzi):
                nuovo = nuovo[:inizio] + corretto + nuovo[fine_p:]
            tot_verde += n_v_tot
        else:
            nuovo, n_v, sel = lavora(originale)
            tot_verde += n_v
            tot_arancio += len(sel)
            selettori += sel

        if nuovo != originale:
            file_toccati += 1
            if applica:
                open(perc, 'w', encoding='utf-8').write(nuovo)

    print(f'verde #1a8f3c -> #188739:        {tot_verde:3d} sostituzioni')
    print(f'bianco -> {TESTO_SU_ARANCIO} sull\'arancione: {tot_arancio:3d} regole')
    print(f'file toccati: {file_toccati}')
    if selettori:
        print('  regole cambiate, ad esempio: ' + ', '.join(sorted(set(selettori))[:6]))
    if not applica:
        print('\n(prova a vuoto: rilancia con --applica)')


if __name__ == '__main__':
    main()
