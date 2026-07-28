#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Avvisa Bing e Copilot che alcune pagine sono cambiate (protocollo IndexNow).

Google non usa IndexNow: per Google si passa dalla Search Console
(Controllo URL -> Richiedi indicizzazione).

Uso:
    python3 indexnow.py                      # le pagine cambiate nell'ultimo commit
    python3 indexnow.py stabilicum.html ...  # solo quelle indicate
    python3 indexnow.py --prova              # mostra cosa manderebbe, senza mandarlo

Prima l'elenco delle pagine era scritto a mano dentro questo file, e invecchiava:
al 28 luglio 2026 conteneva `spanu-stabilicum.html`, che non esiste piu'. Ora le
pagine si ricavano da git, e ognuna viene controllata: se il file non c'e', non
parte. Meglio non avvisare che segnalare un indirizzo morto.
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

KEY = "4bb4591fa00166eacb3cfeccea85e890"
HOST = "partecipazione-attiva.it"
BASE = os.path.dirname(os.path.abspath(__file__))

PROVA = '--prova' in sys.argv
pagine = [a for a in sys.argv[1:] if not a.startswith('--')]

if not pagine:
    # pagine html toccate dall'ultimo commit
    try:
        out = subprocess.run(
            ['git', '-C', BASE, 'diff', '--name-only', 'HEAD~1', 'HEAD'],
            capture_output=True, text=True, timeout=30)
        pagine = [r for r in out.stdout.split()
                  if r.endswith('.html') and '/' not in r]
    except Exception as e:
        sys.exit(f'Non riesco a leggere l\'ultimo commit: {e}')
    if not pagine:
        sys.exit('L\'ultimo commit non ha toccato nessuna pagina html. '
                 'Indica tu le pagine: python3 indexnow.py stabilicum.html')

# ogni pagina deve esistere davvero
esistono, mancano = [], []
for p in pagine:
    (esistono if os.path.isfile(os.path.join(BASE, p)) else mancano).append(p)
for p in mancano:
    print(f'  salto {p}: il file non esiste')
if not esistono:
    sys.exit('Nessuna pagina valida da segnalare.')

if not os.path.isfile(os.path.join(BASE, f'{KEY}.txt')):
    sys.exit(f'STOP: manca il file chiave {KEY}.txt nella radice del sito.')

urls = [f'https://{HOST}/{p}' for p in esistono]
for u in urls:
    print(f'  {u}')

if PROVA:
    print(f'\nProva a vuoto: {len(urls)} URL pronti, non inviati.')
    sys.exit(0)

req = urllib.request.Request(
    'https://api.indexnow.org/indexnow',
    data=json.dumps({
        'host': HOST,
        'key': KEY,
        'keyLocation': f'https://{HOST}/{KEY}.txt',
        'urlList': urls,
    }).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST')
try:
    resp = urllib.request.urlopen(req, timeout=30)
    print(f'\nInviati {len(urls)} URL a IndexNow — risposta {resp.status} {resp.reason}')
except urllib.error.HTTPError as e:
    print(f'\nErrore: {e.code} {e.reason}')
    sys.exit(1)
