#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Costruisce/aggiorna l'indice articoli (articoli.json) scandendo i file con
# schema "@type": "NewsArticle". Fonte di verita' per i "correlati per tema".
import re, json, glob, os, html as H, sys

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
if len(sys.argv) > 1: BASE = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1] + '/'
OUT = BASE + 'articoli.json'

def tema_key(s):
    s = H.unescape(s or '')
    s = re.sub(r'^[^0-9A-Za-zÀ-ÿ]+', '', s).strip()   # toglie emoji/spazi iniziali
    return re.sub(r'\s+', ' ', s).strip().lower()

def campo(h, pat, flags=0):
    m = re.search(pat, h, flags); return m.group(1).strip() if m else None

articoli = []
for p in sorted(glob.glob(BASE + '*.html')):
    h = open(p, encoding='utf-8').read()
    if '"@type": "NewsArticle"' not in h and '"@type":"NewsArticle"' not in h:
        continue
    slug = os.path.basename(p)
    titolo = H.unescape(re.sub(r'\s*\|\s*[^|]*$', '', campo(h, r'<title>([^<]*)</title>') or ''))
    cat = campo(h, r'<div class="categoria">([^<]*)</div>') or ''
    data = campo(h, r'(20\d\d-\d\d-\d\d)')
    img = campo(h, r'<meta property="og:image" content="[^"]*?/([^"/]+)"') or ''
    somm = H.unescape(campo(h, r'<meta name="description" content="([^"]*)"') or '')[:150]
    articoli.append({
        'slug': slug, 'titolo': titolo,
        'tema': H.unescape(cat).strip(), 'tema_key': tema_key(cat),
        'data': data or '', 'img': img, 'sommario': somm,
    })

articoli.sort(key=lambda a: a['data'], reverse=True)   # piu' recenti prima
json.dump({'articoli': articoli}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'OK articoli.json: {len(articoli)} articoli indicizzati')
temi = {}
for a in articoli: temi[a['tema_key']] = temi.get(a['tema_key'], 0) + 1
print('temi trovati:', ', '.join(f'{k}({v})' for k, v in sorted(temi.items(), key=lambda x: -x[1])))
