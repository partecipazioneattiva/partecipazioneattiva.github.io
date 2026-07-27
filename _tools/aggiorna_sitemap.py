#!/usr/bin/env python3
"""Rimette nella sitemap le pagine pubbliche che ne erano rimaste fuori.

Il motore di pubblicazione aggiunge alla sitemap ogni ARTICOLO nuovo, ma le
pagine-strumento nate per altre vie non ci sono mai entrate: misurato il
26/07/2026, mancavano 11 pagine vere, fra cui la Mappa, il WebTV, l'archivio e
"Diritto alla casa". Per Google quelle pagine esistono solo se qualcuno le
linka: nella sitemap non c'erano.

Restano fuori, ed e' giusto: le pagine marcate noindex (bozze e moduli), la
pagina 404 e i file di verifica di Google.

    python3 _tools/aggiorna_sitemap.py            # mostra
    python3 _tools/aggiorna_sitemap.py --applica  # scrive
"""
import datetime
import glob
import os
import re
import sys

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
SITO = 'https://partecipazione-attiva.it/'
SITEMAP = BASE + 'sitemap.xml'
ESCLUSE = re.compile(r'^(404\.html|google[0-9a-f]+\.html|template\.html)$')


def pubbliche():
    fuori = []
    for perc in sorted(glob.glob(BASE + '*.html')):
        nome = os.path.basename(perc)
        if ESCLUSE.match(nome):
            continue
        s = open(perc, encoding='utf-8').read()
        if re.search(r'name=["\']?robots["\']?[^>]*noindex', s, re.I):
            continue
        fuori.append(nome)
    return fuori


def main():
    applica = '--applica' in sys.argv
    xml = open(SITEMAP, encoding='utf-8').read()
    dentro = set(re.findall(r'<loc>[^<]*?/([^/<]+\.html)</loc>', xml))
    mancanti = [n for n in pubbliche() if n not in dentro]
    fantasmi = [n for n in dentro if not os.path.exists(BASE + n)]

    print(f'sitemap: {len(dentro)} voci · pagine pubbliche: {len(pubbliche())}')
    print(f'da aggiungere: {len(mancanti)} -> {mancanti}')
    if fantasmi:
        print(f'voci che puntano a file inesistenti: {fantasmi}')
    if not mancanti or not applica:
        if not applica:
            print('\n(prova a vuoto: rilancia con --applica)')
        return

    voci = []
    for n in mancanti:
        data = datetime.date.fromtimestamp(os.path.getmtime(BASE + n)).isoformat()
        voci.append(f'<url>\n    <loc>{SITO}{n}</loc>\n    <lastmod>{data}</lastmod>\n'
                    f'    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>')
    xml = xml.replace('</urlset>', '\n'.join(voci) + '\n</urlset>')
    open(SITEMAP, 'w', encoding='utf-8').write(xml)

    # verifica: il file deve restare XML valido e contenere tutte le pagine
    import xml.etree.ElementTree as ET
    try:
        ET.parse(SITEMAP)
        stato = 'XML valido'
    except ET.ParseError as e:
        stato = f'XML ROTTO: {e}'
    dopo = set(re.findall(r'<loc>[^<]*?/([^/<]+\.html)</loc>',
                          open(SITEMAP, encoding='utf-8').read()))
    print(f'\nscritto: {len(dopo)} voci · {stato} · '
          f'pagine pubbliche fuori: {len([n for n in pubbliche() if n not in dopo])}')


if __name__ == '__main__':
    main()
