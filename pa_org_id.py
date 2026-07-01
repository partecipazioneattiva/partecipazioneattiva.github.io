#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# A2: aggiunge un @id stabile "#org" all'entita' principale (PoliticalParty su index,
# Organization su chi-siamo e organigramma), per unificarle in un unico nodo del grafo.
# NON tocca gli Organization annidati come publisher (quelli non aprono col @context).
# Idempotente, con assert di unicita'.
import sys

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
if len(sys.argv) > 1: BASE = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1] + '/'
OID = '"@id":"https://partecipazione-attiva.it/#org",'

# pagina -> ancora (apertura dell'entita' principale, subito dopo @type)
TARGET = {
    'index.html':        '{"@context":"https://schema.org","@type":"PoliticalParty",',
    'chi-siamo.html':    '{"@context":"https://schema.org","@type":"Organization",',
    'organigramma.html': '{"@context":"https://schema.org","@type":"Organization",',
}

for slug, anchor in TARGET.items():
    p = BASE + slug
    h = open(p, encoding='utf-8').read()
    if OID in h:
        print(f'{slug}: @id #org gia presente, salto')
        continue
    c = h.count(anchor)
    assert c == 1, f'STOP {slug}: ancora entita principale trovata {c} volte (attesa 1)'
    # inserisco @id subito dopo il @type (cioe' dopo l'ancora)
    h = h.replace(anchor, anchor + OID, 1)
    # verifica: @id presente una sola volta
    assert h.count(OID) == 1, f'STOP {slug}: @id inserito {h.count(OID)} volte'
    open(p, 'w', encoding='utf-8').write(h)
    print(f'{slug}: @id "#org" aggiunto alla entita principale')
