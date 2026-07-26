#!/usr/bin/env python3
"""Precalcola gli embedding delle FAQ per l'assistente PensAttivo.

I vettori delle FAQ si calcolano QUI, una volta, sul Mac: nel browser del
visitatore si calcola solo il vettore della sua domanda (1 conto, non N+1).

Modello: multilingual-e5-small, versione ONNX int8. Non e' nel repo (118 MB,
sopra il limite di 100 MB per file di GitHub): si scarica una volta con
    mkdir -p _modelli/e5-small && cd _modelli/e5-small
    B=https://huggingface.co/Xenova/multilingual-e5-small/resolve/main
    curl -sSLO $B/onnx/model_int8.onnx -o model_int8.onnx
    for f in tokenizer.json tokenizer_config.json config.json special_tokens_map.json; do curl -sSL $B/$f -o $f; done

MISURATO il 26/07/2026, contro le assunzioni dell'incarico:

- int8 (118 MB) e fp32 (470 MB) danno la stessa qualita': 10/18 contro 11/18
  sulle domande di prova. Non serve un modello grande: si usa l'int8.
- La soglia assoluta di similarita' 0,75 prevista dall'incarico NON funziona.
  Le similarita' di e5 sono schiacciate in alto: domande in tema da 0,835,
  domande fuori tema fino a 0,836. Si sovrappongono. "ricetta della pizza
  margherita" superava 0,75 e avrebbe ricevuto una risposta di PA.
- Funziona invece il punteggio z (quanto il primo risultato spicca sulla media
  di tutti) insieme alle frasi ESCA di _dati/esche.json. Da 10/18 a 19/20.
- Si restituiscono i 3 migliori candidati, non una risposta secca: le domande
  che non centrano la FAQ esatta al primo colpo la trovano al secondo.

Lo stesso modello int8 va usato nel browser: vettori calcolati con
quantizzazioni diverse non sono confrontabili fra loro.

    python3 _tools/costruisci_assistente.py                  # solo FAQ approvate
    python3 _tools/costruisci_assistente.py --includi-bozze  # per le prove locali
"""
import base64
import json
import os
import sys

import numpy as np

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
MODELLO = BASE + '_modelli/e5-small/'
USCITA = BASE + 'assistente/faq.json'

# Quanto il primo risultato deve spiccare sulla media perche' si risponda.
# Tarato sulle domande di prova: 2,6 rifiuta il fuori tema senza perdere le
# domande buone (la piu' debole in tema stava a 2,77).
SOGLIA_Z = 2.6


def carica_modello():
    import onnxruntime as ort
    from transformers import AutoTokenizer
    if not os.path.exists(MODELLO + 'model_int8.onnx'):
        sys.exit('STOP: manca il modello. Vedi le istruzioni in cima a questo file.')
    tok = AutoTokenizer.from_pretrained(MODELLO)
    ses = ort.InferenceSession(MODELLO + 'model_int8.onnx',
                               providers=['CPUExecutionProvider'])
    return tok, ses, {i.name for i in ses.get_inputs()}


def vettori(testi, prefisso, tok, ses, nomi):
    """e5 vuole i prefissi "query: " e "passage: " e l'average pooling:
    senza, la qualita' crolla."""
    fuori = []
    for i in range(0, len(testi), 32):
        lotto = [prefisso + t for t in testi[i:i + 32]]
        b = tok(lotto, padding=True, truncation=True, max_length=192,
                return_tensors='np')
        inp = {k: v.astype(np.int64) for k, v in b.items() if k in nomi}
        if 'token_type_ids' in nomi and 'token_type_ids' not in inp:
            inp['token_type_ids'] = np.zeros_like(inp['input_ids'])
        out = ses.run(None, inp)[0]
        m = b['attention_mask'][..., None].astype(np.float32)
        v = (out * m).sum(1) / np.maximum(m.sum(1), 1e-9)
        fuori.append(v / np.linalg.norm(v, axis=1, keepdims=True))
    return np.vstack(fuori)


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

    frasi, righe = [], []
    for f in faq:
        for t in [f['domanda']] + f.get('varianti', []):
            frasi.append(t)
            righe.append(f['id'])
    for e in esche:
        frasi.append(e)
        righe.append('_esca')

    tok, ses, nomi = carica_modello()
    V = vettori(frasi, 'passage: ', tok, ses, nomi)

    # int8: i vettori sono normalizzati, quindi stanno in [-1,1]. 384 byte per
    # vettore invece di 1536, e la differenza sul punteggio e' trascurabile.
    q = np.clip(np.round(V * 127), -127, 127).astype(np.int8)

    os.makedirs(os.path.dirname(USCITA), exist_ok=True)
    fuoriuscita = {
        'modello': 'Xenova/multilingual-e5-small (onnx int8)',
        'dim': int(V.shape[1]),
        'soglia_z': SOGLIA_Z,
        'scala': 1 / 127,
        'righe': righe,
        # Le frasi in chiaro servono al confronto lessicale, che e' il primo
        # livello e funziona subito, senza scaricare il modello.
        'frasi_testo': frasi,
        'vettori_int8_base64': base64.b64encode(q.tobytes()).decode(),
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
    print(f'frasi indicizzate: {len(frasi)} ({len(frasi)-len(esche)} FAQ + {len(esche)} esche)')
    print(f'vettori: {V.shape[0]}x{V.shape[1]} int8')
    print(f'scritto: assistente/faq.json ({peso:.0f} KB)')
    if bozze:
        print('\nATTENZIONE: include FAQ non approvate dal direttivo.')
        print('NON pubblicare questo file: rilancia senza --includi-bozze prima del push.')


if __name__ == '__main__':
    main()
