#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Alleggerisce il menu DESKTOP: rimuove le voci ridondanti "News FB" e "YouTube"
# (gia presenti in topbar e footer). Le versioni del menu MOBILE (con onclick=chiudi())
# restano intatte. Site-wide, idempotente.
import glob, os, sys

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
if len(sys.argv) > 1: BASE = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1] + '/'

# stringhe ESATTE del menu desktop (il mobile ha onclick=chiudi(), quindi non combacia)
TARGETS = [
    '<a href=#blog>News FB</a>',
    '<a href=https://www.youtube.com/@partecipazioneattiva target=_blank rel="noopener noreferrer">YouTube</a>',
]

tot_file = tot_rim = 0
for p in sorted(glob.glob(BASE + '*.html')):
    h = open(p, encoding='utf-8').read()
    a = h.find('<nav')
    b = h.find('</nav>', a)
    if a < 0 or b < 0:
        continue                              # pagina senza navbar: salta
    nav = h[a:b]                              # SOLO il blocco <nav>...</nav>
    rimosse = 0
    for t in TARGETS:
        c = nav.count(t)                      # nel mobile le stesse voci hanno onclick=chiudi() -> non combaciano
        if c:
            assert c == 1, f'STOP {os.path.basename(p)}: "{t[:24]}..." nel <nav> trovata {c} volte (attesa 1)'
            nav = nav.replace(t, '', 1)
            rimosse += 1
    if rimosse:
        h = h[:a] + nav + h[b:]
        open(p, 'w', encoding='utf-8').write(h)
        print(f'  {os.path.basename(p):48} -{rimosse}')
        tot_file += 1; tot_rim += rimosse
print(f'--- rimosse {tot_rim} voci dal menu desktop in {tot_file} pagine ---')
