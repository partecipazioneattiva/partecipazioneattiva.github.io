#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Ripunta i link di menu href=#chisiamo -> chi-siamo.html SOLO in index.html,
# preservando: (a) il bottone hero (ha style=... rimane ancora alla sezione),
# (b) la sezione id=chisiamo della home. Idempotente, con assert.
import os, sys

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'
if len(sys.argv) > 1: BASE = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1] + '/'
IDX = BASE + 'index.html'

h = open(IDX, encoding='utf-8').read()

# 1) il bottone HERO ha una firma unica (style con la pillola): lo "proteggo"
HERO = '<a href=#chisiamo style="background:0 0;color:#fff;padding:13px 30px;border-radius:50px;text-decoration:none;font-weight:700;font-size:.9em;border:2px solid rgba(255,255,255,.7)">Chi siamo</a>'
SENTINEL = '<a href=#PA_HERO_CHISIAMO'   # placeholder temporaneo
assert h.count(HERO) == 1, f'STOP: bottone hero non trovato o non unico ({h.count(HERO)})'
h = h.replace(HERO, HERO.replace('href=#chisiamo', SENTINEL), 1)

# 2) tutti gli ALTRI href=#chisiamo (nav desktop, menu mobile, footer) -> pagina
n_before = h.count('href=#chisiamo')
assert n_before == 3, f'STOP: attesi 3 link di menu da ripuntare, trovati {n_before}'
h = h.replace('href=#chisiamo', 'href=chi-siamo.html')

# 3) ripristino il bottone hero (torna ancora alla sezione)
h = h.replace(SENTINEL, '<a href=#chisiamo')

# verifiche finali
assert h.count('href=chi-siamo.html') >= 3, 'STOP: ripuntamento non applicato'
assert 'id=chisiamo class=fade-in' in h, 'STOP: la sezione id=chisiamo e sparita!'
assert h.count(HERO) == 1, 'STOP: il bottone hero non e stato ripristinato correttamente'

open(IDX, 'w', encoding='utf-8').write(h)
print('OK index.html:')
print('  - nav desktop, menu mobile, footer -> chi-siamo.html (3 link)')
print('  - bottone hero -> resta #chisiamo (sezione home)')
print('  - sezione id=chisiamo: intatta')
