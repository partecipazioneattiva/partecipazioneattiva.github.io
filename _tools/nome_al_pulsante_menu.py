#!/usr/bin/env python3
"""Da' un nome al pulsante del menu a panino, per chi il sito lo ascolta.

MISURATO il 19/08/2026 con pa11y: su 61 pulsanti del menu, 44 non avevano
alcun nome leggibile da un lettore vocale. Il pulsante e' fatto di tre <span>
vuoti — le tre righe del panino — quindi chi non vede sente soltanto
"pulsante", senza sapere che apre il menu. E' una violazione WCAG 4.1.2
(Nome, ruolo, valore), la piu' comune del web e una delle piu' facili da
chiudere.

Non si era vista prima perche' le prove di accessibilita' si erano fatte
sulla home, che e' fra le 17 pagine gia' a posto.

Si scrive "Apri menu" perche' e' la formula che le altre 17 usano gia':
due etichette diverse per lo stesso pulsante confondono piu' di una sola.

    python3 _tools/nome_al_pulsante_menu.py            # mostra
    python3 _tools/nome_al_pulsante_menu.py --applica  # scrive
"""
import glob
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
ETICHETTA = 'Apri menu'

# class=burger con o senza virgolette: meta' dell'HTML di questo sito e'
# minificato senza, ed e' la trappola che fa fallire i controlli scritti
# di fretta.
PULSANTE = re.compile(r'<button(?![^>]*aria-label)([^>]*\bclass=["\']?burger\b[^>]*)>', re.I)


def main():
    applica = '--applica' in sys.argv
    tocchi = pagine = 0

    for perc in sorted(glob.glob(BASE + '*.html')):
        testo = open(perc, encoding='utf-8', errors='ignore').read()
        nuovo, n = PULSANTE.subn(
            lambda m: '<button aria-label="%s"%s>' % (ETICHETTA, m.group(1)), testo)
        if not n:
            continue
        pagine += 1
        tocchi += n
        print('   🔊 %-50s %d pulsante/i' % (os.path.basename(perc), n))
        if applica:
            open(perc, 'w', encoding='utf-8').write(nuovo)

    if not tocchi:
        print('   ✅ tutti i pulsanti del menu hanno gia\' un nome')
    elif applica:
        print('   ✅ dato il nome a %d pulsanti su %d pagine' % (tocchi, pagine))
    else:
        print('\n   %d pulsanti senza nome su %d pagine' % (tocchi, pagine))
        print('   ℹ️  prova a vuoto: rilancia con --applica per scrivere')


if __name__ == '__main__':
    main()
