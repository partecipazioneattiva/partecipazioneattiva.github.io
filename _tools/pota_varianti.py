#!/usr/bin/env python3
"""Pota le varianti generate che fanno piu' male che bene.

Una parafrasi generata serve solo se, cercata da sola, riporta alla PROPRIA
FAQ. Se ne riporta un'altra (o un'esca) e' rumore: non aiuta chi la scriverebbe
e in piu' ruba le domande alle FAQ vicine. E' il filtro che in letteratura si
chiama doc2query-- ("when less is more", Gospodinov 2023): filtrare le query
generate migliora il risultato E alleggerisce l'indice.

Il criterio non guarda MAI le domande di prova: decide l'indice su se' stesso,
quindi la misura su _tools/valuta/domande_prova.json resta onesta.

    python3 _tools/pota_varianti.py            # mostra cosa toglierebbe
    python3 _tools/pota_varianti.py --applica  # riscrive _dati/varianti_auto.json
"""
import json
import shutil
import sys

sys.path.insert(0, '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/_tools/valuta')
from prova_motore import BASE, Indice, costruisci, parole, K1, B  # noqa: E402

AUTO = BASE + '_dati/varianti_auto.json'


def vincitore(ind, i, qt):
    """Chi vince la frase i, escludendo la frase stessa dall'indice."""
    best = {}
    for j in range(ind.n):
        if j == i:
            continue
        s = 0.0
        for p in qt:
            f = ind.tf[j].get(p)
            if not f:
                continue
            s += ind.idf(p) * f * (K1 + 1) / (
                f + K1 * (1 - B + B * ind.lung[j] / ind.media))
        if s > 0:
            rid = ind.righe[j]
            best[rid] = max(best.get(rid, 0.0), s)
    return max(best, key=lambda k: best[k]) if best else None


def main():
    applica = '--applica' in sys.argv
    dati = json.load(open(BASE + '_dati/faq.json', encoding='utf-8'))
    esche = json.load(open(BASE + '_dati/esche.json', encoding='utf-8'))['esche']
    blob = json.load(open(AUTO, encoding='utf-8'))
    auto = blob['varianti']
    faq = [f for f in dati['faq'] if f.get('approvato')]

    ind = costruisci(faq, esche, auto=auto)

    # Quali righe dell'indice sono varianti generate (le uniche potabili: le
    # domande e le varianti scritte a mano non si toccano).
    generata = {}
    k = 0
    for f in faq:
        k += 1 + len(f.get('varianti', []))
        for v in auto.get(f['id'], []):
            generata[k] = (f['id'], v)
            k += 1

    tenute, buttate = {f['id']: [] for f in faq}, []
    for i, (fid, testo) in generata.items():
        v = vincitore(ind, i, parole(testo))
        if v == fid:
            tenute[fid].append(testo)
        else:
            buttate.append((fid, testo, v or 'nessuno'))

    prima = sum(len(v) for v in auto.values())
    dopo = sum(len(v) for v in tenute.values())
    print(f'varianti generate: {prima}  ->  {dopo} tenute, {len(buttate)} potate')
    vuote = [k for k, v in tenute.items() if not v]
    if vuote:
        print(f'ATTENZIONE: {len(vuote)} FAQ restano senza varianti generate: '
              + ', '.join(vuote))
    print('\nEsempi di quel che si butta (variante -> chi se la prendeva):')
    for fid, testo, v in buttate[:12]:
        print(f'  [{fid}] "{testo}"  ->  {v}')

    if not applica:
        print('\n(prova a vuoto: rilancia con --applica per riscrivere il file)')
        return
    shutil.copy(AUTO, AUTO + '.intero')
    blob['varianti'] = tenute
    blob['_potatura'] = (f'{prima} generate, {dopo} tenute: si conservano solo le '
                         f'varianti che, cercate da sole, ritrovano la propria FAQ '
                         f'(doc2query--). Le scartate sono in varianti_auto.json.intero.')
    with open(AUTO, 'w', encoding='utf-8') as g:
        json.dump(blob, g, ensure_ascii=False, indent=1)
    print(f'\nriscritto {AUTO} (copia intera in varianti_auto.json.intero)')


if __name__ == '__main__':
    main()
