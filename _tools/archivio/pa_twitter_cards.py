#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A3 — Completa le Twitter Cards mancanti derivando i valori dagli og:* già
presenti su ogni pagina (og:title -> twitter:title, ecc). Nessun valore
inventato. Salta le pagine gia' complete e 404.html (esclusa di proposito).
"""
import re, glob, os

BASE = os.path.expanduser('~/Desktop/LAVORI/partecipazioneattiva/')
os.chdir(BASE)

def get_og(h, prop):
    m = re.search(r'property=.?og:' + prop + r'.? content="([^"]*)"', h)
    return m.group(1) if m else None

def has_twitter(h, name):
    return f'name="twitter:{name}"' in h or f'name=twitter:{name}' in h

pages = [f for f in glob.glob('*.html') if '<title>' in open(f, encoding='utf-8').read()]
pages = [f for f in pages if f != '404.html']  # esclusa: niente og completo, non serve nei social

aggiornate = 0
saltate = 0

for f in pages:
    h = open(f, encoding='utf-8').read()
    orig = h

    og_title = get_og(h, 'title')
    og_desc  = get_og(h, 'description')
    og_image = get_og(h, 'image')

    if not (og_title and og_desc and og_image):
        print(f'  skip {f}: og incompleto (sorgente mancante)')
        saltate += 1
        continue

    if has_twitter(h, 'title') and has_twitter(h, 'description') and has_twitter(h, 'image') and has_twitter(h, 'card'):
        saltate += 1
        continue

    da_aggiungere = []
    if not has_twitter(h, 'card'):
        da_aggiungere.append(f'<meta name="twitter:card" content="summary_large_image">')
    if not has_twitter(h, 'title'):
        da_aggiungere.append(f'<meta name="twitter:title" content="{og_title}">')
    if not has_twitter(h, 'description'):
        da_aggiungere.append(f'<meta name="twitter:description" content="{og_desc}">')
    if not has_twitter(h, 'image'):
        da_aggiungere.append(f'<meta name="twitter:image" content="{og_image}">')

    if not da_aggiungere:
        saltate += 1
        continue

    blocco = '\n'.join(da_aggiungere)

    # Ancora: subito dopo twitter:card esistente, se c'e'; altrimenti dopo </title>
    m = re.search(r'<meta name=.?twitter:card.? content="[^"]*">', h)
    if m:
        assert h.count(m.group(0)) == 1, f'STOP {f}: twitter:card non univoco'
        h = h.replace(m.group(0), m.group(0) + '\n' + blocco, 1)
    else:
        assert h.count('</title>') == 1, f'STOP {f}: </title> non univoco'
        h = h.replace('</title>', '</title>\n' + blocco, 1)

    assert h != orig, f'STOP {f}: nessuna modifica applicata'
    open(f, 'w', encoding='utf-8').write(h)
    print(f'  {f}: +{len(da_aggiungere)} tag twitter (da og:*)')
    aggiornate += 1

print(f'\n--- Twitter Cards completate su {aggiornate} pagine (saltate: {saltate}) ---')
