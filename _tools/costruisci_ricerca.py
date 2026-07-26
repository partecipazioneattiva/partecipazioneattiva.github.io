#!/usr/bin/env python3
"""Costruisce l'indice Pagefind escludendo le pagine non-contenuto.

Si indicizza da una copia in /tmp perche' Pagefind prende tutti gli .html,
GOLD compreso (il 26/07/2026 template.html usciva nei risultati). Mettere
data-pagefind-ignore nel GOLD non funziona: finirebbe in ogni articolo
generato e sparirebbe tutto il sito dalla ricerca.

Runtime: python3 -m pagefind, NON npx. Node qui e' installato ma rotto
(manca libsimdjson.30.dylib). Installato con:
    pip3 install --user "pagefind[extended]"

    python3 _tools/costruisci_ricerca.py
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'

# Pagine che NON sono contenuto: fuori dall'indice.
FUORI = {
    'template.html',    # il GOLD: modello, non una pagina del sito
    'conferma.html',    # pagine di servizio della Mappa (hanno noindex)
    'cancella.html',
    'contatto.html',
}


def escludi(nome):
    return nome in FUORI or nome.startswith('google')


def noindex(path):
    """Una pagina noindex e' nascosta a Google di proposito (bozze in attesa di
    approvazione). Deve stare fuori anche dalla ricerca interna: il 26/07/2026
    due bozze [BOZZA] PensAttivo uscivano fra i risultati del sito pubblico."""
    with open(path, encoding='utf-8', errors='ignore') as f:
        return 'noindex' in f.read(6000)


def main():
    pagine, escluse = [], []
    for p in sorted(glob.glob(BASE + '*.html')):
        n = os.path.basename(p)
        if escludi(n):
            escluse.append((n, 'non e\' contenuto'))
        elif noindex(p):
            escluse.append((n, 'noindex: nascosta di proposito'))
        else:
            pagine.append(p)

    with tempfile.TemporaryDirectory(prefix='pa-indice-') as tmp:
        for p in pagine:
            shutil.copy(p, os.path.join(tmp, os.path.basename(p)))

        out = BASE + 'pagefind'
        r = subprocess.run(
            [sys.executable, '-m', 'pagefind', '--site', tmp, '--output-path', out],
            capture_output=True, text=True)

        righe = [l for l in (r.stdout + r.stderr).splitlines()
                 if 'Indexed' in l or 'error' in l.lower()]
        for l in righe:
            print(' ', l.strip())
        if r.returncode != 0:
            print('\nERRORE: pagefind e\' uscito con codice', r.returncode)
            print(r.stdout[-1500:], r.stderr[-1500:])
            sys.exit(1)

    print(f'\npagine indicizzate: {len(pagine)}')
    print(f'pagine escluse:     {len(escluse)}')
    for n, perche in escluse:
        print(f'   {n:44} {perche}')
    print(f'indice scritto in:  {BASE}pagefind')


if __name__ == '__main__':
    main()
