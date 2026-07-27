#!/usr/bin/env python3
import os
# -*- coding: utf-8 -*-
# Fix mirati: #1 schema curriculum, #6 llms.txt, #7 link mobile Iscriviti.
# Ogni modifica ha count->assert. Idempotente dove possibile.
import re, sys

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'
if len(sys.argv) > 1: BASE = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1] + '/'

# ---------- #1 CURRICULUM: rimuovi i 2 blocchi ld+json impropri ----------
CV = BASE + 'curriculum-luigi-spanu.html'
h = open(CV, encoding='utf-8').read()

def rimuovi_blocco(html, firma_inizio):
    a = html.find(firma_inizio)
    assert a >= 0, f'STOP curriculum: firma non trovata: {firma_inizio[:50]}'
    b = html.find('</script>', a)
    assert b >= 0, 'STOP curriculum: </script> mancante'
    b += len('</script>')
    # inghiotto eventuale newline residua
    seg = html[a:b]
    return html[:a] + html[b:], seg

n_before = len(re.findall(r'<script type=.{0,3}application/ld\+json', h))
if n_before > 0:
    h, b1 = rimuovi_blocco(h, '<script type=application/ld+json>{"@context":"https://schema.org","@type":"NewsArticle"')
    h, b2 = rimuovi_blocco(h, '<script type="application/ld+json">{"@context": "https://schema.org", "@type": "FAQPage"')
    n_after = len(re.findall(r'<script type=.{0,3}application/ld\+json', h))
    assert n_after == 0, f'STOP curriculum: restano {n_after} blocchi ld+json (attesi 0)'
    open(CV, 'w', encoding='utf-8').write(h)
    print(f'#1 curriculum: rimossi 2 blocchi schema (NewsArticle+FAQPage) -> ld+json residui: {n_after}')
else:
    print('#1 curriculum: nessun blocco ld+json (gia pulito)')

# ---------- #7 MOBILE ISCRIVITI: ripunta SOLO la voce del menu mobile ----------
IDX = BASE + 'index.html'
h = open(IDX, encoding='utf-8').read()
FORM = 'https://docs.google.com/forms/d/e/1FAIpQLSdUJHaPB9o6gA7TXHNLNgsKcftZjwCsjepZ3r_C9TH2ODsr3A/viewform'
MOB_OLD = '<a href=#iscriviti onclick=chiudi()>Iscriviti</a>'
MOB_NEW = f'<a href={FORM} target=_blank rel="noopener noreferrer" onclick=chiudi()>Iscriviti</a>'
c = h.count(MOB_OLD)
if c:
    assert c == 1, f'STOP index: voce mobile Iscriviti trovata {c} volte (attesa 1)'
    h = h.replace(MOB_OLD, MOB_NEW, 1)
    open(IDX, 'w', encoding='utf-8').write(h)
    print('#7 mobile Iscriviti: menu mobile -> Google Form (hero e sezione #iscriviti intatti)')
else:
    print('#7 mobile Iscriviti: gia sistemato o non trovato')

# ---------- #6 LLMS.TXT: aggiungi i 2 articoli mancanti ----------
LL = BASE + 'llms.txt'
t = open(LL, encoding='utf-8').read()
B = 'https://partecipazione-attiva.it/'
righe = [
    ('importanza-sport-giovani.html',
     '- [Lo sport come strumento di crescita e inclusione per i giovani](' + B + 'importanza-sport-giovani.html): Analisi PA su sport, giovani e comunita'),
    ('costruire-comunita-roma-2026.html',
     '- [Costruire comunita: il modello di partecipazione dal basso a Roma](' + B + 'costruire-comunita-roma-2026.html): Resoconto e prospettive dei gruppi territoriali del Lazio'),
]
aggiunte = 0
for slug, riga in righe:
    if slug in t:
        continue
    # inserisco dopo l'ultima riga che e' una voce lista "- [" per restare nella sezione articoli
    idx = t.rfind('\n- [')
    if idx < 0:
        t = t.rstrip() + '\n' + riga + '\n'
    else:
        fine_riga = t.find('\n', idx + 1)
        fine_riga = len(t) if fine_riga < 0 else fine_riga
        t = t[:fine_riga] + '\n' + riga + t[fine_riga:]
    aggiunte += 1
if aggiunte:
    open(LL, 'w', encoding='utf-8').write(t)
print(f'#6 llms.txt: {aggiunte} articoli aggiunti')
