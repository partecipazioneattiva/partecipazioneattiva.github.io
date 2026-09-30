#!/usr/bin/env python3
"""I pulsanti «condividi» (Facebook, WhatsApp) devono condividere LA PAGINA IN CUI STANNO.

30/09/2026: nove pagine nate dal GOLD (che deriva da spanu-sire.html) condividevano
ancora `spanu-sire.html`: chi premeva «condividi» sulla Rete APE mandava in giro
l'articolo sul SIRE. Nessun controllo lo vedeva, perche' il link non e' rotto.

    python3 _tools/condividi_se_stessa.py            # mostra (uscita 1 se trova difetti)
    python3 _tools/condividi_se_stessa.py --applica  # corregge
"""
import glob
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
SITO = 'https://partecipazione-attiva.it/'
SALTA = {'template.html'}
# l'indirizzo condiviso, dentro un link a Facebook o a WhatsApp
SCHEMA = re.compile(r'((?:sharer\.php\?u=|wa\.me/\?text=[^"\'>\s]*?))' + re.escape(SITO) + r'([A-Za-z0-9_.-]*)')


def main():
    applica = '--applica' in sys.argv
    difetti = 0
    for percorso in sorted(glob.glob(BASE + '*.html')):
        nome = os.path.basename(percorso)
        if nome in SALTA or nome.startswith('google'):
            continue
        testo = open(percorso, encoding='utf-8').read()
        giusto = '' if nome == 'index.html' else nome
        sbagliati = [m.group(2) for m in SCHEMA.finditer(testo) if m.group(2) != giusto]
        if not sbagliati:
            continue
        difetti += len(sbagliati)
        print(f'{nome}: {len(sbagliati)} pulsanti condividono «{sbagliati[0]}»')
        if applica:
            nuovo = SCHEMA.sub(lambda m: m.group(1) + SITO + giusto, testo)
            assert len(SCHEMA.findall(nuovo)) == len(SCHEMA.findall(testo))
            open(percorso, 'w', encoding='utf-8').write(nuovo)
    print(f'\n{difetti} pulsanti da correggere' + (' — corretti' if applica and difetti else ''))
    sys.exit(1 if difetti and not applica else 0)


if __name__ == '__main__':
    main()
