#!/usr/bin/env python3
"""
pa_chisiamo_deploy.py
1. Copia chi-siamo.html nel repo
2. Aggiorna link "Chi Siamo" navbar in tutte le pagine (index.html#chisiamo → chi-siamo.html)
3. Aggiunge chi-siamo.html a sitemap.xml
4. Aggiunge voce a llms.txt
"""
import os, re, shutil, glob

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva'
SRC  = os.path.join(BASE, 'chi-siamo.html')

# ── 0. Verifica che chi-siamo.html esiste nel repo ──
assert os.path.exists(SRC), f'STOP: chi-siamo.html non trovato in {BASE}'
print('OK chi-siamo.html presente nel repo')

def read(p):
    with open(p, encoding='utf-8') as f: return f.read()
def write(p, c):
    with open(p, 'w', encoding='utf-8') as f: f.write(c)

# ── 1. Aggiorna link navbar in tutte le pagine HTML (esclusa chi-siamo.html stessa) ──
HTML_FILES = [f for f in glob.glob(os.path.join(BASE, '*.html'))
              if os.path.basename(f) != 'chi-siamo.html'
              and os.path.basename(f) not in ('404.html', 'googled83ce80b766b7708.html')]

OLD_LINKS = [
    'href="index.html#chisiamo"',
    "href='index.html#chisiamo'",
    'href=index.html#chisiamo',
]
NEW_LINK = 'href="chi-siamo.html"'

updated_nav = []
for fpath in sorted(HTML_FILES):
    h = read(fpath)
    changed = False
    for old in OLD_LINKS:
        if old in h:
            h = h.replace(old, NEW_LINK)
            changed = True
    if changed:
        write(fpath, h)
        updated_nav.append(os.path.basename(fpath))

print(f'OK navbar: link "Chi Siamo" aggiornato in {len(updated_nav)} pagine')
if updated_nav:
    for f in updated_nav[:5]: print(f'  → {f}')
    if len(updated_nav) > 5: print(f'  ... e altri {len(updated_nav)-5}')

# ── 2. Sitemap: aggiunge chi-siamo.html ──
sitemap_path = os.path.join(BASE, 'sitemap.xml')
sm = read(sitemap_path)
URL = 'https://partecipazione-attiva.it/chi-siamo.html'
if URL not in sm:
    new_entry = f'<url><loc>{URL}</loc><lastmod>2026-07-01</lastmod></url>'
    assert sm.count('</urlset>') == 1, 'STOP: </urlset> non univoco in sitemap'
    sm = sm.replace('</urlset>', new_entry + '\n</urlset>')
    assert URL in sm, 'STOP: URL non inserito in sitemap'
    write(sitemap_path, sm)
    print('OK sitemap.xml: chi-siamo.html aggiunta')
else:
    print('OK sitemap.xml: chi-siamo.html già presente')

# ── 3. llms.txt: aggiunge voce pagina istituzionale ──
llms_path = os.path.join(BASE, 'llms.txt')
llms = read(llms_path)
VOCE = '- [Chi Siamo](https://partecipazione-attiva.it/chi-siamo.html): Fondazione 2021, missione, valori, battaglie, organigramma — pagina istituzionale'
if 'chi-siamo.html' not in llms:
    anchor = '## Articoli e analisi'
    assert llms.count(anchor) == 1, 'STOP: ancora llms.txt non univoca'
    llms = llms.replace(anchor, '## Pagine principali aggiuntive\n\n' + VOCE + '\n\n' + anchor)
    write(llms_path, llms)
    print('OK llms.txt: voce Chi Siamo aggiunta')
else:
    print('OK llms.txt: chi-siamo già presente')

print('\n--- FATTO. Ora verifica in Safari e poi PUSH ---')
