#!/usr/bin/env python3
"""Costruisce assistente/faq.json, l'unico file che l'assistente scarica.

Dentro ci vanno le FAQ approvate, le loro frasi (domanda + varianti scritte a
mano + varianti generate in locale) e le esche. Il motore e' BM25 e gira nel
browser sul testo: nessun modello da scaricare, nessun vettore.

PERCHE' NIENTE MODELLO SEMANTICO (misurato il 26/07/2026, banco a 38 domande
in _tools/valuta/domande_prova.json, sempre a recall@1):

    BM25, indice iniziale                              32/38  (84%)
    BM25 + parafrasi generate in locale                35/38  (92%)
    multilingual-e5-small int8 nel browser             37/38  (97%)

Le 5 domande di differenza costerebbero al visitatore ~37 MB di modello
(dopo averne potato il vocabolario) piu' il motore ONNX in WebAssembly, su un
sito che leggono soprattutto pensionati col telefono. Le parafrasi danno quasi
tutto il guadagno a costo zero di banda. Se un giorno si volesse il semantico,
il modello e le misure sono nel MANUALE_WEB.

    python3 _tools/costruisci_assistente.py                  # solo FAQ approvate
    python3 _tools/costruisci_assistente.py --includi-bozze  # per le prove locali
"""
import json
import os
import sys

BASE = '/Users/osxssd/Desktop/ARCHIVIO GENERALE/LAVORI/partecipazioneattiva/'
USCITA = BASE + 'assistente/faq.json'


def main():
    bozze = '--includi-bozze' in sys.argv
    dati = json.load(open(BASE + '_dati/faq.json', encoding='utf-8'))
    esche = json.load(open(BASE + '_dati/esche.json', encoding='utf-8'))['esche']

    tutte = dati['faq']
    faq = tutte if bozze else [f for f in tutte if f.get('approvato')]
    fuori = len(tutte) - len(faq)
    if not faq:
        print(f'ATTENZIONE: 0 FAQ approvate su {len(tutte)}: l\'assistente non ha')
        print('nulla da dire. Il direttivo deve rivedere _dati/faq.json e mettere')
        print('"approvato": true sulle voci accettate.')
        if not bozze:
            print('\nPer provarlo in locale intanto: --includi-bozze')
            return

    # Varianti generate in locale (_tools/genera_varianti.py): allargano l'indice
    # con i modi diversi di chiedere la stessa cosa. Non si mostrano mai al
    # visitatore, servono solo a far combaciare la sua domanda con la FAQ giusta.
    auto = {}
    perc_auto = BASE + '_dati/varianti_auto.json'
    if os.path.exists(perc_auto):
        auto = json.load(open(perc_auto, encoding='utf-8'))['varianti']

    frasi, righe = [], []
    for f in faq:
        for t in [f['domanda']] + f.get('varianti', []) + auto.get(f['id'], []):
            frasi.append(t)
            righe.append(f['id'])
    for e in esche:
        frasi.append(e)
        righe.append('_esca')

    os.makedirs(os.path.dirname(USCITA), exist_ok=True)
    fuoriuscita = {
        'motore': 'BM25 su frasi + varianti generate in locale',
        'righe': righe,
        # Le frasi in chiaro sono tutto quel che serve a BM25: nessun modello
        # da scaricare, nessun vettore.
        'frasi_testo': frasi,
        'faq': [{'id': f['id'], 'tema': f['tema'], 'domanda': f['domanda'],
                 'risposta': f['risposta'], 'link': f['link']} for f in faq],
        'suggerite': [f['domanda'] for f in faq[:6]],
        'bozze_incluse': bozze,
    }
    with open(USCITA, 'w', encoding='utf-8') as f:
        json.dump(fuoriuscita, f, ensure_ascii=False, separators=(',', ':'))

    peso = os.path.getsize(USCITA) / 1024
    print(f'FAQ pubblicate:  {len(faq)}' + (f' (+{fuori} non approvate, escluse)'
                                            if fuori and not bozze else ''))
    generate = sum(len(v) for v in auto.values())
    print(f'frasi indicizzate: {len(frasi)} ({len(frasi)-len(esche)} FAQ '
          f'(di cui {generate} varianti generate) + {len(esche)} esche)')
    print(f'scritto: assistente/faq.json ({peso:.0f} KB)')
    if bozze:
        print('\nATTENZIONE: include FAQ non approvate dal direttivo.')
        print('NON pubblicare questo file: rilancia senza --includi-bozze prima del push.')


if __name__ == '__main__':
    main()
