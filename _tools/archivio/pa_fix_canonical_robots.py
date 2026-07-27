#!/usr/bin/env python3
import os
# -*- coding: utf-8 -*-
# PASSO 1 (fix certi, basso rischio):
#   - 3 canonical errati (puntano a spanu-sire.html) -> puntano a se stessi
#   - robots.txt: Sitemap dal dominio github.io -> dominio .it
# Ogni modifica ha count->assert. Idempotente.
import sys

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'
if len(sys.argv) > 1: BASE = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1] + '/'
U = 'https://partecipazione-attiva.it/'

# --- canonical: pagina -> se stessa ---
PAGINE = [
    'stabilicum-aggiornamento-28maggio2026.html',
    'rcauto-campania-mozione-maggio2026.html',
    'curriculum-luigi-spanu.html',
]
WRONG = '<link rel="canonical" href="https://partecipazione-attiva.it/spanu-sire.html">'
for slug in PAGINE:
    p = BASE + slug
    h = open(p, encoding='utf-8').read()
    right = f'<link rel="canonical" href="{U}{slug}">'
    if right in h:
        print(f'{slug}: canonical gia corretto, salto')
        continue
    c = h.count(WRONG)
    assert c == 1, f'STOP {slug}: canonical errato trovato {c} volte (attesa 1)'
    h = h.replace(WRONG, right, 1)
    open(p, 'w', encoding='utf-8').write(h)
    print(f'{slug}: canonical -> se stesso')

# --- robots.txt: dominio sitemap ---
rp = BASE + 'robots.txt'
r = open(rp, encoding='utf-8').read()
OLD = 'Sitemap: https://partecipazioneattiva.github.io/sitemap.xml'
NEW = 'Sitemap: https://partecipazione-attiva.it/sitemap.xml'
if NEW in r:
    print('robots.txt: sitemap gia sul dominio .it, salto')
else:
    c = r.count(OLD)
    assert c == 1, f'STOP robots.txt: riga sitemap github.io trovata {c} volte (attesa 1)'
    r = r.replace(OLD, NEW, 1)
    open(rp, 'w', encoding='utf-8').write(r)
    print('robots.txt: Sitemap -> https://partecipazione-attiva.it/sitemap.xml')
