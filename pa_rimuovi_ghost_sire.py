#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PASSO 2: rimuove SOLO il blocco ld+json "ghost" (headline SIRE) dalle 9 pagine.
# Preserva ogni altro blocco (NewsArticle corretto / FAQPage / BreadcrumbList).
# Con assert: in ogni pagina deve esserci ESATTAMENTE 1 blocco ghost.
import re, sys

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
if len(sys.argv) > 1: BASE = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1] + '/'

PAGINE = ['rete-ape.html','rcauto-aggiornamento-maggio2026.html','cristiano-sanita.html',
          'stabilicum-aggiornamento-28maggio2026.html','sanita-ocse-maggio2026.html',
          'regione-lazio.html','regione-campania.html','rcauto-campania-mozione-maggio2026.html',
          'crosetto-diagnosi-precoce-3dcbs.html']

GHOST = 'Proposta di legge SIRE'
PAT = re.compile(r'<script[^>]*ld\+json[^>]*>.*?</script>', re.S)

for slug in PAGINE:
    p = BASE + slug
    h = open(p, encoding='utf-8').read()
    blocks = PAT.findall(h)
    ghost_blocks = [b for b in blocks if GHOST in b]
    if not ghost_blocks:
        print(f'{slug}: nessun ghost (gia pulito), salto')
        continue
    assert len(ghost_blocks) == 1, f'STOP {slug}: {len(ghost_blocks)} blocchi ghost (atteso 1)'
    g = ghost_blocks[0]
    assert h.count(g) == 1, f'STOP {slug}: blocco ghost non univoco nel file'
    tot_before = len(blocks)
    # rimuovo il blocco ghost + eventuale whitespace/newline immediatamente adiacente
    h2 = h.replace(g, '', 1)
    # verifica: un blocco in meno, e nessun ghost residuo
    after = PAT.findall(h2)
    assert len(after) == tot_before - 1, f'STOP {slug}: conteggio blocchi errato dopo rimozione'
    assert not any(GHOST in b for b in after), f'STOP {slug}: ghost ancora presente'
    open(p, 'w', encoding='utf-8').write(h2)
    print(f'{slug}: ghost rimosso  ({tot_before} -> {len(after)} blocchi ld+json)')
