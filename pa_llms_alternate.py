#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# A7: aggiunge <link rel="alternate" type="text/plain" href=".../llms.txt"> nel <head>
# di ogni pagina, ancorandolo dopo </title> (ancora presente su tutte le pagine reali).
# Salta i file senza <title> (es. googled...html di verifica) e chi ce l'ha gia.
# Idempotente, con assert di unicita' dell'ancora.
import glob, os, sys

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'
if len(sys.argv) > 1: BASE = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1] + '/'

LINK = '<link rel="alternate" type="text/plain" href="https://partecipazione-attiva.it/llms.txt" title="llms.txt">'
MARK = 'type="text/plain" href="https://partecipazione-attiva.it/llms.txt"'

agg = salt = 0
for p in sorted(glob.glob(BASE + '*.html')):
    slug = os.path.basename(p)
    h = open(p, encoding='utf-8').read()
    if MARK in h:
        salt += 1; continue                      # gia presente
    if h.count('</title>') != 1:
        print(f'  skip {slug}: </title> assente o non unico ({h.count("</title>")})')
        salt += 1; continue
    h = h.replace('</title>', '</title>' + LINK, 1)
    assert h.count(MARK) == 1, f'STOP {slug}: link inserito {h.count(MARK)} volte'
    open(p, 'w', encoding='utf-8').write(h)
    agg += 1
print(f'--- alternate llms.txt aggiunto a {agg} pagine (saltate: {salt}) ---')
