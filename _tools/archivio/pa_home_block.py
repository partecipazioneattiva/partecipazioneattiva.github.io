#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Inserisce in home, prima del footer, il blocco "Cosa facciamo + numeri + come aiutare".
# Il numero di analisi e' letto da articoli.json (veritiero). Solo index.html.
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'
if len(sys.argv) > 1: BASE = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1] + '/'
IDX = BASE + 'index.html'

# numero analisi dall'indice (fallback prudente)
n = 0
try:
    n = len(json.load(open(BASE + 'articoli.json', encoding='utf-8')).get('articoli', []))
except Exception:
    pass
n_txt = str(n) if n else '29'

ISCR = 'https://docs.google.com/forms/d/e/1FAIpQLSdUJHaPB9o6gA7TXHNLNgsKcftZjwCsjepZ3r_C9TH2ODsr3A/viewform'

def stat(num, lab):
    return ('<div style="text-align:center;min-width:120px">'
            f'<div style="font-family:montserrat,sans-serif;font-size:1.7em;font-weight:900;color:#8a4e00;line-height:1">{num}</div>'
            f'<div style="font-family:montserrat,sans-serif;font-size:.8em;font-weight:700;color:#9c5b00;'
            'text-transform:uppercase;letter-spacing:.5px;margin-top:6px">' + lab + '</div></div>')

def cta(href, extra, titolo, sub):
    return (f'<a href="{href}" {extra} style="display:block;flex:1 1 280px;max-width:340px;text-decoration:none;'
            'border-radius:16px;padding:18px 22px;text-align:center">'
            f'<span style="font-family:montserrat,sans-serif;font-weight:900;font-size:1.05em">{titolo}</span>'
            f'<span style="display:block;font-family:merriweather,serif;font-size:.85em;font-weight:400;'
            f'margin-top:6px;opacity:.9">{sub}</span></a>')

BLOCK = (
'<section id="pa-cosa-facciamo" data-pa-section="cosa-facciamo" style="background:#fff8ee;border-top:3px solid #ffd580;padding:52px 24px">'
'<div style="max-width:980px;margin:0 auto;text-align:center">'
'<h2 style="font-family:montserrat,sans-serif;color:#8a4e00;font-size:1.5em;font-weight:800;letter-spacing:.5px;margin:0 0 12px">Cosa facciamo</h2>'
'<p style="font-family:merriweather,serif;color:#333;font-size:1.05em;line-height:1.7;max-width:680px;margin:0 auto 30px">'
'Partecipazione Attiva è un <strong>movimento popolare di cittadini</strong>, libero e senza appartenenze di partito. '
'Produciamo <strong>analisi indipendenti</strong> e portiamo avanti <strong>battaglie concrete</strong> &mdash; voto, sanità, territori, diritti.</p>'
'<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:28px;margin-bottom:36px">'
+ stat('Dal 2021', 'fondazione')
+ stat('Campania e Lazio', 'territori attivi')
+ stat(f'<span id="pa-num-analisi">{n_txt}</span>', 'analisi e approfondimenti')
+ '</div>'
'<h3 style="font-family:montserrat,sans-serif;color:#8a4e00;font-size:1.05em;font-weight:800;text-transform:uppercase;letter-spacing:.5px;margin:0 0 18px">Come puoi aiutare</h3>'
'<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:16px">'
+ cta(ISCR, 'target="_blank" rel="noopener noreferrer"',
      'Iscriviti — è gratis &rarr;', 'Entra nel movimento e partecipa alle decisioni.')
      .replace('text-align:center"', 'text-align:center;background:#9c5b00;color:#fff"')
+ cta('#', 'onclick="apriSostienici(event)"',
      'Sostienici', 'Finanzia analisi e campagne indipendenti.')
      .replace('text-align:center"', 'text-align:center;background:#fff;color:#9c5b00;border:2px solid #9c5b00"')
+ '</div></div></section>')

ANCHOR = '<footer data-pa-section="footer"'
html = open(IDX, encoding='utf-8').read()
assert 'id="pa-cosa-facciamo"' not in html, 'STOP: blocco gia presente'
assert html.count(ANCHOR) == 1, f'STOP: ancora footer {html.count(ANCHOR)} (attesa 1)'
html = html.replace(ANCHOR, BLOCK + ANCHOR, 1)
open(IDX, 'w', encoding='utf-8').write(html)
print(f'OK blocco "Cosa facciamo" inserito prima del footer (numero analisi: {n_txt})')
