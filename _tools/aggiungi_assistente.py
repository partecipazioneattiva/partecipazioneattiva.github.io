#!/usr/bin/env python3
"""Aggiunge l'assistente PensAttivo a tutte le pagine del sito.

Il sito non ha template condivisi: ogni pagina si porta la propria copia. Per
non dover ritoccare 60 file a ogni modifica del widget, qui si inserisce SOLO
un tag <script>: tutto il resto (icona, box, stile, logica) vive in
assistente/pensattivo.js, che si cambia in un punto solo.

Idempotente: se il tag c'e' gia', non lo duplica.

    python3 _tools/aggiungi_assistente.py            # mostra cosa farebbe
    python3 _tools/aggiungi_assistente.py --applica   # scrive
"""
import glob
import os
import re
import sys

BASE = '/Users/osxssd/Desktop/ARCHIVIO GENERALE/LAVORI/partecipazioneattiva/'

# Fuori: il GOLD e i file di verifica Google (non sono pagine del sito).
# Dentro invece le pagine di servizio della Mappa: chi ci arriva per un
# problema deve poter chiedere aiuto.
def escludi(nome):
    return nome == 'template.html' or nome.startswith('google')


MARCA = 'assistente/pensattivo.js'


def profondita(nome):
    """Tutte le pagine stanno nella radice del sito, ma se un giorno ce ne
    fossero in sottocartelle il percorso relativo va corretto."""
    return ''


def main():
    applica = '--applica' in sys.argv
    fatte, gia, problemi = [], [], []

    for percorso in sorted(glob.glob(BASE + '*.html')):
        nome = os.path.basename(percorso)
        if escludi(nome):
            continue
        with open(percorso, encoding='utf-8') as f:
            html = f.read()

        if MARCA in html:
            gia.append(nome)
            continue
        tag = ('<script src="' + profondita(nome) + MARCA
               + '" defer data-pagefind-ignore></script>')
        if '</body>' in html:
            nuovo = html.replace('</body>', tag + '\n</body>', 1)
        elif '</html>' in html:
            nuovo = html.replace('</html>', tag + '\n</html>', 1)
        else:
            problemi.append((nome, 'non trovo </body> ne </html>'))
            continue

        if applica:
            with open(percorso, 'w', encoding='utf-8') as f:
                f.write(nuovo)
        fatte.append(nome)

    print(f'assistente aggiunto: {len(fatte)}')
    for n in fatte[:8]:
        print(f'   {n}')
    if len(fatte) > 8:
        print(f'   ... e altre {len(fatte)-8}')
    if gia:
        print(f'gia\' presente su: {len(gia)} pagine')
    if problemi:
        print(f'PROBLEMI: {len(problemi)}')
        for n, p in problemi:
            print(f'   {n}: {p}')
    if not applica and fatte:
        print('\n(prova a vuoto: rilancia con --applica per scrivere)')


if __name__ == '__main__':
    main()
