#!/usr/bin/env python3
"""Misura pagina per pagina se le correzioni di contrasto hanno MIGLIORATO, e
riporta indietro quelle che hanno peggiorato.

    python3 _tools/verifica_contrasti.py                # solo misura
    python3 _tools/verifica_contrasti.py --ripristina   # e annulla i peggioramenti

------------------------------------------------------------------------------
PERCHE' ESISTE — la lezione del 2 agosto 2026
------------------------------------------------------------------------------
`correggi_contrasti.py` decide se un testo e' troppo chiaro guardando il fondo
**dichiarato accanto** al colore. Ma nell'HTML il fondo quasi sempre non e'
dichiarato li': si eredita da un elemento piu' esterno. Su `sanitapubblica.html`
alcuni link stavano su una fascia scura ereditata: scurendoli "per migliorare
l'accessibilita'" il loro contrasto e' passato da 4,12 a **1,38** — cioe' quasi
invisibili. Il conto totale dei difetti restava identico e non si sarebbe visto
niente.

Da qui la regola: **il contrasto vero lo sa solo il browser**, che conosce il
fondo ereditato. Percio' non ci si fida del calcolo sul testo: si misura con
pa11y prima e dopo, pagina per pagina, e si tiene solo cio' che e' migliorato.

Una pagina si tiene se **entrambe** le cose sono vere:
  - i difetti sono diminuiti (o erano gia' zero);
  - il rapporto PEGGIORE della pagina non e' sceso.
La seconda condizione e' quella che conta: senza, un cambio che trasforma
cinque difetti lievi in un difetto gravissimo passerebbe per un miglioramento.

Richiede pa11y (`npm install -g pa11y`) e il ramo `main` come termine di paragone.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RIFERIMENTO = 'main'


def esamina(percorso_file):
    """Ritorna (numero di difetti, rapporto peggiore). None se pa11y non parte."""
    try:
        r = subprocess.run(['pa11y', '--reporter', 'json', 'file://' + percorso_file],
                           capture_output=True, text=True, timeout=180)
        difetti = json.loads(r.stdout or '[]')
    except Exception:
        return None
    rapporti = [float(m.group(1)) for d in difetti
                if (m := re.search(r'ratio of ([\d.]+):1', d.get('message', '')))]
    return len(difetti), (min(rapporti) if rapporti else 99.0)


def main():
    ripristina = '--ripristina' in sys.argv
    pagine = sorted(f for f in os.listdir(BASE) if f.endswith('.html'))
    tenute, annullate, saltate = [], [], []
    tot_prima = tot_dopo = 0

    with tempfile.TemporaryDirectory() as tmp:
        for i, pagina in enumerate(pagine, 1):
            vecchia = subprocess.run(['git', '-C', BASE, 'show', f'{RIFERIMENTO}:{pagina}'],
                                     capture_output=True, text=True)
            if vecchia.returncode != 0:
                saltate.append(pagina)          # pagina nuova: niente con cui confrontarla
                continue
            copia = os.path.join(tmp, pagina)
            open(copia, 'w', encoding='utf-8').write(vecchia.stdout)

            prima = esamina(copia)
            dopo = esamina(os.path.join(BASE, pagina))
            if prima is None or dopo is None:
                saltate.append(pagina)
                continue

            n_prima, peggio_prima = prima
            n_dopo, peggio_dopo = dopo
            tot_prima += n_prima
            tot_dopo += n_dopo

            migliorata = n_dopo <= n_prima and peggio_dopo >= peggio_prima - .01
            segno = '  ok  ' if migliorata else 'ANNULLA'
            print(f'{i:3d}/{len(pagine)} {segno} {pagina:<46} '
                  f'{n_prima:3d} -> {n_dopo:3d} difetti   '
                  f'peggior rapporto {peggio_prima:.2f} -> {peggio_dopo:.2f}')

            if migliorata:
                tenute.append(pagina)
            else:
                annullate.append(pagina)
                if ripristina:
                    subprocess.run(['git', '-C', BASE, 'checkout', RIFERIMENTO, '--', pagina])
                    tot_dopo += n_prima - n_dopo

    print('\n' + '=' * 74)
    print(f'pagine migliorate e tenute: {len(tenute)}')
    print(f'pagine peggiorate:          {len(annullate)}' +
          ('  (riportate indietro)' if ripristina else '  (usa --ripristina)'))
    if saltate:
        print(f'pagine saltate (nuove):     {len(saltate)}')
    print(f'difetti totali: {tot_prima} -> {tot_dopo}')
    if annullate:
        print('  da rivedere a mano: ' + ', '.join(annullate[:8]))


if __name__ == '__main__':
    main()
