#!/usr/bin/env python3
import os
# -*- coding: utf-8 -*-
# Aggiunge la meta description (assente) alle due pagine regione, subito dopo <title>.
# Chirurgico, idempotente, con assert.
import sys

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'
if len(sys.argv) > 1: BASE = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1] + '/'

PAGINE = {
    'regione-lazio.html': (
        '<title>Partecipazione Attiva nel Lazio | Partecipazione Attiva</title>',
        'Partecipazione Attiva nel Lazio: gruppi attivi a Roma, Ladispoli e Guidonia Montecelio. '
        'Scopri le attività e unisciti al movimento civico dei cittadini nella tua città.'
    ),
    'regione-campania.html': (
        '<title>Partecipazione Attiva in Campania | Partecipazione Attiva</title>',
        'Partecipazione Attiva in Campania: gruppo attivo a Napoli e sul territorio. '
        'Scopri le nostre battaglie civiche e unisciti al movimento dei cittadini.'
    ),
}

for fname, (title, desc) in PAGINE.items():
    p = BASE + fname
    h = open(p, encoding='utf-8').read()
    if 'name=description' in h or 'name="description"' in h:
        print(f'{fname}: description gia presente, salto')
        continue
    assert h.count(title) == 1, f'STOP {fname}: <title> non trovato o non unico ({h.count(title)})'
    meta = f'<meta name=description content="{desc}">'
    h = h.replace(title, title + meta, 1)
    open(p, 'w', encoding='utf-8').write(h)
    print(f'{fname}: meta description aggiunta ({len(desc)} char)')
