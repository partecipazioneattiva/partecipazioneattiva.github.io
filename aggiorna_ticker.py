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

# ⚠️ NON agganciarsi alla stringa esatta del tag.
# Fino al 28/07/2026 qui c'era l'apertura scritta per intero, attributo per
# attributo. Poi al div e' stato aggiunto `data-pagefind-ignore` (per tenere la
# barra fuori dalla ricerca) e da quel momento lo script non trovava piu'
# niente: si fermava sull'assert e il ticker non si poteva piu' rigenerare.
# Ora si cerca l'id e si risale al `<div` che lo contiene, cosi' gli attributi
# possono cambiare di numero e di ordine senza rompere niente.
import re as _re

def trova_tk(html):
    """(inizio_contenuto, fine_contenuto) del div #tk, comunque sia scritto.

    ⚠️ Le virgolette nel pattern NON sono opzionali, e c'e' un motivo.
    Il 28/07/2026 il pattern era `id\\s*=\\s*["\\']?tk["\\']?`: con le
    virgolette facoltative agganciava anche **id="tkpause"**, il bottone di
    pausa, che nel sorgente viene PRIMA del ticker. Lo script ha riscritto il
    blocco sbagliato e ha cancellato mezza intestazione della home.
    Qui le virgolette sono obbligatorie e devono chiudere subito dopo `tk`.
    """
    m = _re.search(r'id\s*=\s*(["\'])tk\1', html)
    if not m:
        raise SystemExit('STOP: nessun elemento con id="tk" in index.html')
    apertura = html.rfind('<div', 0, m.start())
    if apertura < 0:
        raise SystemExit('STOP: id="tk" non e\' dentro un <div>')
    i = html.index('>', m.end()) + 1
    j = html.index('</div>', i)
    return i, j

NOVITA = BASE + 'novita.json'
MESI = ('gennaio febbraio marzo aprile maggio giugno luglio agosto '
        'settembre ottobre novembre dicembre').split()

def voce_html(v):
    return f'{v["emoji"]} <strong>{v["tema"]}:</strong> {v["testo"]}'

def voce_novita():
    """La nuova uscita apre il giro, ed e' l'unica voce CLICCABILE.

    Sta qui e non in aggiorna_novita.py apposta: il ticker deve avere UN SOLO
    scrittore. Due script che riscrivono la stessa regione di index.html sono
    la ricetta per cancellarsi a vicenda — e le voci qui dentro vanno
    triplicate (il JS usa scrollWidth/3), quindi un inserimento fatto da fuori
    finirebbe in un terzo solo del giro.
    """
    if not os.path.exists(NOVITA):
        return None
    n = json.load(open(NOVITA, encoding='utf-8')).get('ultima')
    if not n or not n.get('titolo'):
        return None
    a, m, g = n['data'].split('-')
    quando = f'{int(g)} {MESI[int(m)-1]} {a}'
    emoji = {'TG': '\U0001F4FA', 'VIDEO': '\U0001F3AC'}.get(n['tipo'].upper(), '\U0001F4F0')
    return (f'{emoji} <strong>{n["etichetta"].upper()}:</strong> '
            f'<a href="{n["link"]}" style="color:#ffd580;text-decoration:underline">'
            f'{n["titolo"]}, {quando}</a>')

d = json.load(open(DATA, encoding='utf-8'))
voci = d.get('voci', [])
assert voci, 'STOP: temi.json senza voci'

pezzi = [voce_html(v) for v in voci]
nov = voce_novita()
if nov:
    pezzi.insert(0, nov)
    print(f'  in testa: {nov[:70]}...')

blocco = SEP.join(pezzi)
contenuto = (blocco + SEP) * 3          # triplicato -> loop continuo

html = open(IDX, encoding='utf-8').read()
i, j = trova_tk(html)
html = html[:i] + contenuto + html[j:]
open(IDX, 'w', encoding='utf-8').write(html)
print(f'OK ticker rigenerato da temi.json: {len(voci)} voci (x3 per il loop)')
for v in voci:
    print(f'  {v["emoji"]} {v["tema"]}')
