#!/usr/bin/env python3
"""Mette la trascrizione dei video dentro la pagina, per renderla cercabile.

Pagefind legge l'HTML: quello che viene detto a voce in un video non e' testo,
quindi non e' cercabile. Il 26/07/2026 cercare una frase pronunciata in un
video non trovava niente: nessuna pagina aveva la trascrizione.

Convenzione: la trascrizione di video/NOME.mp4 sta in video/NOME.txt.
Si genera con vtrascrivi (whisper.cpp large-v3-turbo, vedi MANUALE_VIDEO):
    vtrascrivi video/NOME.mp4

DUE SCELTE, entrambe deliberate:

1. NIENTE data-pagefind-body, anche se l'incarico lo suggeriva. Pagefind ha una
   regola pericolosa: se anche UNA sola pagina del sito ha data-pagefind-body,
   tutte le pagine che non l'hanno vengono escluse dall'indice. Metterlo qui
   avrebbe cancellato dalla ricerca le altre 56 pagine. La trascrizione e'
   testo normale nel body: viene indicizzata comunque, senza rischi.

2. Trascrizione VISIBILE in un <details> richiudibile, non nascosta. Serve a
   chi e' sordo o guarda senza audio, e per chi preferisce leggere. Testo
   nascosto ai visitatori ma dato ai motori di ricerca e' inoltre una pratica
   che Google considera cloaking.

Idempotente: un marcatore per video evita di accumulare un blocco a ogni
esecuzione (era gia' successo con le lenti in navbar, 3 su azioni.html).

    python3 _tools/trascrizioni_ricerca.py            # mostra cosa farebbe
    python3 _tools/trascrizioni_ricerca.py --applica   # scrive
"""
import glob
import os
import re
import sys

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
SALTA = {'template.html'}

# <source src="video/x.mp4"> oppure <video ... src="video/x.mp4">
VIDEO = re.compile(r'(?:src)\s*=\s*["\']([^"\']*?([^"\'/]+)\.mp4)["\']', re.I)

BLOCCO = '''
<!-- pa-trascrizione:{nome} -->
<details class="pa-trascr">
  <summary>Trascrizione del video</summary>
  <div class="pa-trascr-testo">
{paragrafi}
  </div>
</details>
'''

STILE = '''<style>
.pa-trascr{margin:18px auto 26px;max-width:720px;border:1px solid #f0dcc0;
  border-radius:12px;background:#fffaf3}
.pa-trascr summary{cursor:pointer;padding:12px 16px;font-family:Montserrat,
  system-ui,sans-serif;font-weight:600;font-size:.95em;color:#8a4e00;
  list-style:none}
.pa-trascr summary::-webkit-details-marker{display:none}
.pa-trascr summary::before{content:"\\25B8";display:inline-block;margin-right:8px;
  color:#e8900a;transition:transform .2s}
.pa-trascr[open] summary::before{transform:rotate(90deg)}
.pa-trascr-testo{padding:0 16px 14px;font-family:Merriweather,Georgia,serif;
  font-size:.94em;line-height:1.75;color:#4a4038}
.pa-trascr-testo p{margin:0 0 10px}
</style>'''


PAROLE_PER_PARAGRAFO = 55


def paragrafi(testo):
    """Whisper manda a capo a caso e spesso non mette punteggiatura: senza
    questo, 142 parole finivano in un unico paragrafo illeggibile. Si spezza
    sui punti quando ci sono, altrimenti a conteggio di parole."""
    piatto = ' '.join(testo.split())
    pezzi = []
    for frase in re.split(r'(?<=[.!?])\s+', piatto):
        parole = frase.split()
        if not parole:
            continue
        # Frase lunghissima (parlato senza punti): si spezza sulle virgole,
        # e se non bastano a conteggio di parole.
        while len(parole) > PAROLE_PER_PARAGRAFO * 1.6:
            taglio = PAROLE_PER_PARAGRAFO
            for i in range(PAROLE_PER_PARAGRAFO, min(len(parole) - 5,
                                                     int(PAROLE_PER_PARAGRAFO * 1.5))):
                if parole[i].endswith(','):
                    taglio = i + 1
                    break
            pezzi.append(' '.join(parole[:taglio]))
            parole = parole[taglio:]
        pezzi.append(' '.join(parole))

    fuori, blocco = [], []
    for p in pezzi:
        blocco.append(p)
        if len(' '.join(blocco).split()) >= PAROLE_PER_PARAGRAFO:
            fuori.append(' '.join(blocco))
            blocco = []
    if blocco:
        fuori.append(' '.join(blocco))
    return '\n'.join(f'    <p>{p}</p>' for p in fuori)


def main():
    applica = '--applica' in sys.argv
    fatti, saltati, senza = [], [], []

    for percorso in sorted(glob.glob(BASE + '*.html')):
        pagina = os.path.basename(percorso)
        if pagina in SALTA:
            continue
        with open(percorso, encoding='utf-8') as f:
            html = f.read()

        nuovo = html
        for rel, nome in VIDEO.findall(html):
            if not rel.lower().endswith('.mp4') or rel.startswith('http'):
                continue
            txt = BASE + os.path.splitext(rel)[0] + '.txt'
            if not os.path.exists(txt):
                senza.append((pagina, rel))
                continue

            # Si rigenera sempre: se la trascrizione viene corretta (whisper
            # sbaglia i nomi propri - "case popolare" per "Base Popolare"), il
            # blocco gia' in pagina deve aggiornarsi, non essere saltato.
            vecchio = re.compile(
                r'\s*<!-- pa-trascrizione:' + re.escape(nome) + r' -->'
                r'.*?</details>\s*', re.S)
            aggiornata = bool(vecchio.search(nuovo))
            nuovo = vecchio.sub('', nuovo)

            testo = open(txt, encoding='utf-8').read().strip()
            if len(testo.split()) < 15:
                saltati.append((pagina, nome, 'trascrizione troppo corta'))
                continue

            blocco = BLOCCO.format(nome=nome, paragrafi=paragrafi(testo))
            # Dopo la </figure> che contiene il video, o dopo il </video>.
            i = nuovo.find(rel)
            chiusura = nuovo.find('</figure>', i)
            if chiusura == -1:
                chiusura = nuovo.find('</video>', i)
                taglio = chiusura + len('</video>')
            else:
                taglio = chiusura + len('</figure>')
            if chiusura == -1:
                saltati.append((pagina, nome, 'non trovo dove inserirlo'))
                continue

            nuovo = nuovo[:taglio] + blocco + nuovo[taglio:]
            if 'pa-trascr{' not in nuovo:
                nuovo = nuovo.replace('</head>', STILE + '\n</head>', 1)
            fatti.append((pagina, nome, len(testo.split()),
                          'aggiornata' if aggiornata else 'inserita'))

        if nuovo != html and applica:
            with open(percorso, 'w', encoding='utf-8') as f:
                f.write(nuovo)

    print(f'trascrizioni in pagina: {len(fatti)}')
    for pagina, nome, parole, come in fatti:
        print(f'   {pagina:44} {nome:34} {parole:4} parole  {come}')
    if saltati:
        print(f'\nsaltati: {len(saltati)}')
        for pagina, nome, perche in saltati:
            print(f'   {pagina:44} {nome:34} {perche}')
    if senza:
        print(f'\nvideo senza trascrizione ({len(senza)}) - lanciare vtrascrivi:')
        for pagina, rel in senza:
            print(f'   {pagina:44} {rel}')
    if not applica and fatti:
        print('\n(prova a vuoto: rilancia con --applica per scrivere)')


if __name__ == '__main__':
    main()
