#!/usr/bin/env python3
"""Porta i caratteri tipografici dentro il sito, togliendoli da Google.

PERCHE': ogni pagina chiedeva i caratteri a fonts.googleapis.com. Per vedere il
testo scritto giusto, il browser di chi legge doveva comunicare il proprio
indirizzo IP a Google, su 63 pagine, senza che nessuno lo avesse chiesto.
Ospitandoli qui, il sito non parla piu' con nessuno alle spalle di chi lo legge
(misura del 26/07/2026, rapporto in _audit/).

In piu' e' piu' veloce: niente terzo dominio da risolvere e contattare prima di
poter disegnare il testo.

Caratteri: Montserrat (400,600,700,800,900) e Merriweather (400,700 + corsivo
400), che sono quelli usati davvero dal CSS delle pagine. Open Sans era
richiesto da una pagina sola e non usato da nessun CSS: lasciato fuori.
Sottoinsiemi: latin e latin-ext (bastano per l'italiano).

    python3 _tools/ospita_caratteri.py           # scarica e scrive fonts/
    python3 _tools/ospita_caratteri.py --pagine  # sostituisce i link nelle pagine
"""
import glob
import os
import re
import sys
import urllib.request

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
CARTELLA = BASE + 'fonts/'
CSS_LOCALE = CARTELLA + 'caratteri.css'
RICHIESTA = ('https://fonts.googleapis.com/css2?'
             'family=Montserrat:wght@400;600;700;800;900&'
             'family=Merriweather:ital,wght@0,400;0,700;1,400&display=swap')
# Serve un'intestazione da browser moderno: senza, Google risponde con i
# vecchi formati (ttf), che pesano il triplo di woff2.
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')
SOTTOINSIEMI = ('latin', 'latin-ext')


def prendi(url, testo=True):
    r = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(r, timeout=30) as f:
        d = f.read()
    return d.decode('utf-8') if testo else d


def scarica():
    os.makedirs(CARTELLA, exist_ok=True)
    css = prendi(RICHIESTA)
    blocchi = re.findall(r'/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})', css, re.S)
    fuori, presi, peso = [], 0, 0
    for sotto, blocco in blocchi:
        if sotto not in SOTTOINSIEMI:
            continue
        fam = re.search(r"font-family:\s*'([^']+)'", blocco).group(1)
        peso_f = re.search(r'font-weight:\s*(\d+)', blocco).group(1)
        stile = 'italic' if 'font-style: italic' in blocco else 'normal'
        url = re.search(r'url\(([^)]+)\)', blocco).group(1)
        nome = f'{fam.lower().replace(" ", "-")}-{peso_f}{"-italic" if stile == "italic" else ""}-{sotto}.woff2'
        dati = prendi(url, testo=False)
        open(CARTELLA + nome, 'wb').write(dati)
        presi += 1
        peso += len(dati)
        intervallo = re.search(r'unicode-range:([^;]+);', blocco)
        fuori.append(f"""@font-face{{font-family:'{fam}';font-style:{stile};
font-weight:{peso_f};font-display:swap;src:url(./{nome}) format('woff2');
unicode-range:{intervallo.group(1).strip() if intervallo else 'U+0-10FFFF'}}}""")
    intestazione = ('/* Caratteri ospitati sul sito, non presi da Google: cosi\' il\n'
                    '   browser di chi legge non comunica il proprio IP a terzi.\n'
                    '   Li rigenera _tools/ospita_caratteri.py */\n')
    open(CSS_LOCALE, 'w', encoding='utf-8').write(intestazione + '\n'.join(fuori) + '\n')
    print(f'scaricati {presi} file ({peso/1024:.0f} KB) in fonts/')
    print(f'scritto fonts/caratteri.css ({os.path.getsize(CSS_LOCALE)/1024:.1f} KB)')


def sostituisci_pagine():
    """Toglie i link a Google e mette quello locale, una volta sola per pagina."""
    link_google = re.compile(
        r'<link[^>]*href=["\']?https://fonts\.(?:googleapis|gstatic)\.com[^>]*>')
    toccate = 0
    for perc in sorted(glob.glob(BASE + '*.html')):
        s = originale = open(perc, encoding='utf-8').read()
        if not link_google.search(s):
            continue
        primo = [True]

        def sost(m):
            if primo[0]:
                primo[0] = False
                return '<link href="fonts/caratteri.css" rel="stylesheet">'
            return ''
        s = link_google.sub(sost, s)
        if s != originale:
            open(perc, 'w', encoding='utf-8').write(s)
            toccate += 1
    print(f'pagine aggiornate: {toccate}')
    resta = [os.path.basename(p) for p in glob.glob(BASE + '*.html')
             if 'fonts.googleapis' in open(p, encoding='utf-8').read()
             or 'fonts.gstatic' in open(p, encoding='utf-8').read()]
    print('VERIFICA: ' + ('nessun riferimento a Google rimasto'
                          if not resta else f'ATTENZIONE, restano: {resta}'))


if __name__ == '__main__':
    if '--pagine' in sys.argv:
        sostituisci_pagine()
    else:
        scarica()
