#!/usr/bin/env python3
"""Scrive in fondo all'archivio l'indice di TUTTE le pagine pubbliche.

Il problema, misurato il 19/08/2026 con Google: otto pagine della sitemap non
erano raggiungibili da nessun collegamento interno del sito
(diritto-alla-casa, esserci, spanu-no-ad-autonomie-maggio2026,
curriculum-luigi-spanu, perche-la-mappa, regione-campania, regione-lazio,
legge-elettorale-giusta). Per Google una pagina che nessuno linka esiste solo
nella sitemap, ed e' il segnale piu' debole che ci sia: di 61 pagine
dichiarate, l'operatore site: ne mostrava 34.

L'indice qui sotto e' un rimedio che non invecchia: si rigenera dalla sitemap,
quindi ogni pagina nuova ci entra da sola. Serve anche ai lettori — e' la
pagina "tutte le pagine" che i siti seri hanno sempre avuto.

    python3 _tools/indice_pagine.py            # mostra cosa cambierebbe
    python3 _tools/indice_pagine.py --applica  # scrive
"""
import html
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
SITO = 'https://partecipazione-attiva.it/'
ARCHIVIO = BASE + 'archivio.html'
SITEMAP = BASE + 'sitemap.xml'

INIZIO = '<!-- INDICE-PAGINE:inizio -->'
FINE = '<!-- INDICE-PAGINE:fine -->'

# Rifiniture del titolo: via la firma del sito, che si ripete su tutte le voci.
CODA = re.compile(r'\s*(\||&#124;|&mdash;|—|-)\s*(Partecipazione Attiva|PensAttivo|PA)\s*$')


def pagine():
    """(file, titolo) di ogni pagina dichiarata nella sitemap."""
    testo = open(SITEMAP, encoding='utf-8').read()
    fuori = []
    for loc in re.findall(r'<loc>' + re.escape(SITO) + r'([^<]*)</loc>', testo):
        nome = loc or 'index.html'
        if not nome.endswith('.html'):
            continue
        perc = BASE + nome
        if not os.path.exists(perc):
            print('   ⚠️  nella sitemap ma il file non c\'e\':', nome)
            continue
        pag = open(perc, encoding='utf-8', errors='ignore').read()
        # Una pagina noindex non va messa in vetrina.
        rob = re.search(r'name=["\']?robots["\']?[^>]*content=["\']?([^">]*)', pag)
        if rob and 'noindex' in rob.group(1):
            continue
        tit = re.search(r'<title>(.*?)</title>', pag, re.S)
        tit = re.sub(r'\s+', ' ', tit.group(1)).strip() if tit else nome
        for _ in range(2):
            tit = CODA.sub('', tit)
        fuori.append((nome, tit))
    # Ordine alfabetico sul titolo come lo legge una persona, non sul codice.
    fuori.sort(key=lambda v: html.unescape(v[1]).lower())
    return fuori


def blocco(voci):
    # Lo stile sta tutto qui dentro, non negli attributi dei tag: una regola
    # scritta nel tag vince sempre sulla media query, e sul telefono l'indice
    # sarebbe rimasto a due colonne strette (misurato a 375 px il 19/08/2026).
    stile = (
        '<style>'
        '#tutte-le-pagine{background:#fff;padding:40px 24px;border-top:3px solid #e8900a}'
        '#tutte-le-pagine .dentro{max-width:900px;margin:0 auto}'
        '#tutte-le-pagine h2{font-family:montserrat,sans-serif;font-size:1.25em;'
        'color:#8a4e00;margin:0 0 6px}'
        '#tutte-le-pagine p{font-family:merriweather,serif;color:#555;'
        'line-height:1.55;margin:0 0 18px}'
        '#tutte-le-pagine ul{columns:2;column-gap:32px;list-style:none;padding:0;margin:0;'
        'font-family:montserrat,sans-serif;font-size:.95em;line-height:1.8}'
        '#tutte-le-pagine li{break-inside:avoid;margin-bottom:6px}'
        '#tutte-le-pagine a{color:#8a4e00;text-decoration:none}'
        '#tutte-le-pagine a:hover,#tutte-le-pagine a:focus{text-decoration:underline}'
        '@media(max-width:700px){#tutte-le-pagine ul{columns:1}'
        '#tutte-le-pagine li{margin-bottom:10px}}'
        '</style>'
    )
    righe = [
        INIZIO,
        stile,
        '<section id="tutte-le-pagine">',
        '<div class="dentro">',
        '<h2>Indice di tutte le pagine</h2>',
        f'<p>Ogni pagina pubblica del sito, in ordine alfabetico. Sono {len(voci)}.</p>',
        '<ul>',
    ]
    for nome, tit in voci:
        righe.append(f'<li><a href="{nome}">{tit}</a></li>')
    righe += ['</ul>', '</div>', '</section>', FINE]
    return '\n'.join(righe)


def main():
    voci = pagine()
    nuovo = blocco(voci)
    testo = open(ARCHIVIO, encoding='utf-8').read()

    if INIZIO in testo:
        vecchio = re.search(re.escape(INIZIO) + r'.*?' + re.escape(FINE), testo, re.S).group(0)
        if vecchio == nuovo:
            print('   ✅ indice gia\' aggiornato — %d pagine' % len(voci))
            return
        testo2 = testo.replace(vecchio, nuovo)
        azione = 'aggiornato'
    else:
        if '</main>' not in testo:
            sys.exit('   ❌ archivio.html non ha </main>: non so dove mettere l\'indice')
        testo2 = testo.replace('</main>', nuovo + '\n</main>', 1)
        azione = 'inserito'

    print('   📄 indice %s in archivio.html — %d pagine' % (azione, len(voci)))
    for nome, tit in voci:
        print('      %-52s %s' % (nome, html.unescape(tit)[:46]))

    if '--applica' in sys.argv:
        open(ARCHIVIO, 'w', encoding='utf-8').write(testo2)
        print('   ✅ scritto')
    else:
        print('   ℹ️  prova a vuoto: rilancia con --applica per scrivere')


if __name__ == '__main__':
    main()
