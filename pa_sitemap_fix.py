#!/usr/bin/env python3
"""
pa_sitemap_fix.py — fix completo sitemap + noindex + llms.txt
Operazioni:
  1. sitemap.xml: rimuove 4 duplicati, aggiunge 4 pagine mancanti,
     corregge lastmod index.html e battaglie.html
  2. spanu-sire.html + diretta-sire.html: aggiunge noindex
  3. llms.txt: aggiunge articoli giugno 2026
"""

import os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
def read(path):
    with open(path, encoding='utf-8') as f: return f.read()

def write(path, content):
    with open(path, 'w', encoding='utf-8') as f: f.write(content)

# ─────────────────────────────────────────
# 1. SITEMAP
# ─────────────────────────────────────────
sitemap_path = os.path.join(BASE, 'sitemap.xml')
sm = read(sitemap_path)

orig_count = sm.count('<loc>')

# 1a. Rimuovi i 4 duplicati (tengo la versione con lastmod più recente)
# Duplicati: cristiano-sanita, spanu-congresso-base-popolare,
#            stabilicum-audizione-maggio2026, territori
# Strategia: ricostruisco la sitemap deduplicata mantenendo l'ultima occorrenza

import xml.etree.ElementTree as ET

# Parse grezzo per non perdere struttura
# Uso regex per estrarre tutti i blocchi <url>...</url>
url_blocks = re.findall(r'<url>.*?</url>', sm, re.DOTALL)

seen = {}
deduped = []
for block in url_blocks:
    loc = re.search(r'<loc>(.*?)</loc>', block)
    if not loc:
        continue
    key = loc.group(1).strip()
    # Teniamo l'ultimo (di solito ha lastmod più aggiornato)
    seen[key] = block

# Ordine: manteniamo l'ordine originale di prima comparsa
order = []
seen_order = set()
for block in url_blocks:
    loc = re.search(r'<loc>(.*?)</loc>', block)
    if not loc: continue
    key = loc.group(1).strip()
    if key not in seen_order:
        seen_order.add(key)
        order.append(key)

deduped_blocks = [seen[k] for k in order]

removed_dups = orig_count - len(deduped_blocks)
assert removed_dups >= 0

# 1b. Aggiungi le 4 pagine mancanti (se non già presenti)
to_add = [
    ('rcauto-campania-mozione-maggio2026.html', '2026-04-03'),
    ('spanu-no-ad-autonomie-maggio2026.html',   '2026-05-28'),
    ('stabilicum-aggiornamento-28maggio2026.html', '2026-05-28'),
    ('curriculum-luigi-spanu.html',             '2026-04-03'),
]

existing_locs = {re.search(r'<loc>(.*?)</loc>', b).group(1) for b in deduped_blocks}

added = []
for slug, lastmod in to_add:
    loc_url = f'https://partecipazione-attiva.it/{slug}'
    if loc_url not in existing_locs:
        new_block = f'<url><loc>{loc_url}</loc><lastmod>{lastmod}</lastmod></url>'
        deduped_blocks.append(new_block)
        added.append(slug)

# 1c. Correggi lastmod di index.html e battaglie.html → oggi
TODAY = '2026-07-01'
fixed_lastmod = []
final_blocks = []
for block in deduped_blocks:
    loc = re.search(r'<loc>(.*?)</loc>', block).group(1)
    if loc in [
        'https://partecipazione-attiva.it/index.html',
        'https://partecipazione-attiva.it/battaglie.html',
    ]:
        # aggiorna o aggiungi lastmod
        if '<lastmod>' in block:
            old = re.search(r'<lastmod>(.*?)</lastmod>', block).group(1)
            if old != TODAY:
                block = re.sub(r'<lastmod>.*?</lastmod>', f'<lastmod>{TODAY}</lastmod>', block)
                fixed_lastmod.append(loc.split('/')[-1])
        else:
            block = block.replace('</url>', f'<lastmod>{TODAY}</lastmod></url>')
            fixed_lastmod.append(loc.split('/')[-1])
    final_blocks.append(block)

# Ricostruisco sitemap
header = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
footer = '\n</urlset>'
new_sm = header + '\n'.join(final_blocks) + footer

# Verifiche
assert new_sm.count('<loc>') == len(final_blocks), 'STOP: conteggio loc sbagliato'
assert new_sm.count('cristiano-sanita') == 1, 'STOP: cristiano-sanita ancora duplicato'
assert new_sm.count('spanu-congresso-base-popolare') == 1, 'STOP: spanu-congresso ancora duplicato'
assert new_sm.count('rcauto-campania-mozione') == 1, 'STOP: rcauto-campania mancante'

write(sitemap_path, new_sm)
print(f'OK sitemap.xml: -{removed_dups} duplicati, +{len(added)} aggiunte, {len(fixed_lastmod)} lastmod corretti')
print(f'  Aggiunte: {added}')
print(f'  Lastmod corretti: {fixed_lastmod}')
print(f'  Totale URL: {len(final_blocks)}')

# ─────────────────────────────────────────
# 2. NOINDEX su spanu-sire.html e diretta-sire.html
# ─────────────────────────────────────────
NOINDEX_TAG = '<meta name="robots" content="noindex,nofollow">'

for fname in ['spanu-sire.html', 'diretta-sire.html']:
    fpath = os.path.join(BASE, fname)
    h = read(fpath)
    if 'noindex' in h:
        print(f'OK {fname}: noindex già presente')
        continue
    # Inserisce dopo <meta charset
    target = re.search(r'<meta charset[^>]+>', h)
    assert target, f'STOP {fname}: nessun meta charset trovato'
    assert h.count(target.group()) == 1, f'STOP {fname}: meta charset non univoco'
    h2 = h.replace(target.group(), target.group() + NOINDEX_TAG, 1)
    assert 'noindex' in h2, f'STOP {fname}: noindex non inserito'
    write(fpath, h2)
    print(f'OK {fname}: noindex aggiunto')

# ─────────────────────────────────────────
# 3. llms.txt — aggiunta articoli giugno 2026
# ─────────────────────────────────────────
llms_path = os.path.join(BASE, 'llms.txt')
llms = read(llms_path)

NEW_ARTICLES = """- [Stabilicum: discussione in Aula Camera, 26 giugno 2026](https://partecipazione-attiva.it/stabilicum-aula-camera-giugno2026.html): Iter accelerato, emendamenti, spaccatura sulle preferenze, udienza Cassazione 29 ottobre
- [RC Auto neopatentati: il 98% del divario Napoli-Milano è nella polizza](https://partecipazione-attiva.it/rcauto-neopatentati-giugno2026.html): Napoli paga 604€, per under-21 la RC è il 71,5% del costo annuo dell'auto
- [Ricorso Rosatellum: udienza Cassazione il 29 ottobre 2026](https://partecipazione-attiva.it/ricorso-rosatellum-cassazione-ottobre2026.html): Prima sezione civile, ricorrenti elettori siciliani
- [Assemblea NO AD Napoli giugno 2026](https://partecipazione-attiva.it/assemblea-noad-napoli-giugno2026.html): Maschio Angioino, Neri, Cristiano, Spanu contro l'autonomia differenziata
- [Resoconto assemblea NO AD Napoli 6 giugno 2026](https://partecipazione-attiva.it/resoconto-assemblea-noad-napoli-6giugno2026.html): Sintesi dei lavori e delle proposte emerse
- [Astensionismo comunali 2026](https://partecipazione-attiva.it/astensionismo-comunali2026.html): Affluenza al 52,07% ai ballottaggi, -8 punti dal primo turno
- [Spanu: NO all'autonomia differenziata — maggio 2026](https://partecipazione-attiva.it/spanu-no-ad-autonomie-maggio2026.html): Analisi e posizione di Luigi Spanu"""

# Inserisco dopo l'ultimo articolo della sezione "Articoli e analisi"
anchor = '## Territorio'
assert llms.count(anchor) == 1, 'STOP llms.txt: ancora non univoca'

# Controlla che gli articoli giugno non siano già presenti
if 'stabilicum-aula-camera-giugno2026' in llms:
    print('OK llms.txt: articoli giugno già presenti, nessuna modifica')
else:
    new_llms = llms.replace(anchor, NEW_ARTICLES + '\n\n' + anchor)
    assert 'stabilicum-aula-camera-giugno2026' in new_llms, 'STOP llms.txt: inserimento fallito'
    # Rimuovi il link rotto spanu-stabilicum.html se presente
    new_llms = re.sub(r'\n- \[Stabilicum: aggiornamento iter parlamentare\].*?Spanu.*?\n', '\n', new_llms)
    write(llms_path, new_llms)
    print('OK llms.txt: 7 articoli giugno aggiunti')

print('\n--- FATTO. Ora esegui il PUSH ---')
