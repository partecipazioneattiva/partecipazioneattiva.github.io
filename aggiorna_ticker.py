#!/usr/bin/env python3
import os
# -*- coding: utf-8 -*-
# Rigenera la barra scorrevole (#tk) della home dalla FONTE DI VERITA' temi.json.
# Le voci sono triplicate per il loop senza stacchi (il JS usa scrollWidth/3).
# Uso:  python3 aggiorna_ticker.py        (agisce sul repo)
import json, sys

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'
if len(sys.argv) > 1: BASE = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1] + '/'
IDX  = BASE + 'index.html'
DATA = BASE + 'temi.json'

SEP = ' &nbsp;&nbsp;&bull;&nbsp;&nbsp; '
TK_OPEN = ('<div id="tk" data-pa-section="ticker" style="position:absolute;'
           'white-space:nowrap;will-change:transform; color:#ffffff;">')

def voce_html(v):
    return f'{v["emoji"]} <strong>{v["tema"]}:</strong> {v["testo"]}'

d = json.load(open(DATA, encoding='utf-8'))
voci = d.get('voci', [])
assert voci, 'STOP: temi.json senza voci'

blocco = SEP.join(voce_html(v) for v in voci)
contenuto = (blocco + SEP) * 3          # triplicato -> loop continuo

html = open(IDX, encoding='utf-8').read()
assert html.count(TK_OPEN) == 1, f'STOP: apertura #tk trovata {html.count(TK_OPEN)} volte (attesa 1)'
i = html.index(TK_OPEN) + len(TK_OPEN)
j = html.index('</div>', i)
html = html[:i] + contenuto + html[j:]
open(IDX, 'w', encoding='utf-8').write(html)
print(f'OK ticker rigenerato da temi.json: {len(voci)} voci (x3 per il loop)')
for v in voci:
    print(f'  {v["emoji"]} {v["tema"]}')
