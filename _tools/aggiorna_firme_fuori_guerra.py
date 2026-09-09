#!/usr/bin/env python3
"""Riallinea il numero di adesioni all'appello "Fuori l'Italia dalla guerra".

Legge il numero vero dall'API del sito (fuorilitaliadallaguerra.org) e lo
riscrive in tre posti:
  · nell'articolo, paragrafo «Di cosa si tratta»: «N adesioni»;
  · nell'articolo, riquadro «I numeri al ...»: «Adesioni indicate sul sito: N»
    e la data;
  · nella home, la card dell'appello: «Oltre N adesioni finora».

COME SI CALCOLA IL NUMERO. Il sito non mostra un contatore ottenuto da
un'unica fonte: la home somma due cose, come si legge nel suo stesso codice
(assets/index-*.js, variabile `totalSigners = totalSubscribers + zo.length`):

  1. `totalSubscribers` — chi si e' iscritto dal modulo. Si legge dall'API
     pubblica del sito: https://fuorilitaliadallaguerra.org/api/index.php
     ?limit=1&page=1 → campo JSON "total". Cresce in tempo reale.
  2. Un elenco fisso di primi firmatari «storici» (il sito lo chiama «primi
     100 promotori»), che al 9 settembre 2026 contava esattamente 100 nomi
     (Moni Ovadia, Carlo Rovelli, ...). Non e' raggiungibile via API: e'
     scritto dentro il pacchetto JavaScript del sito.

⚠️ PRIMI_FIRMATARI qui sotto e' quel secondo numero, **fissato a mano** il
9 settembre 2026 leggendo il codice del sito. Se un giorno il sito aggiungesse
o togliesse nomi da quell'elenco iniziale, il totale calcolato qui si
scosterebbe da quello mostrato in home di quella stessa quantita' — un caso
raro (e' un elenco di fondazione, non il modulo di adesione corrente), ma se
capitasse **il sintomo e' un divario stabile e ripetuto** fra il nostro
numero e quello della home: in quel caso si riverifica leggendo di nuovo il
bundle JS del sito (cercare la costante assegnata a `totalSigners`), non si
cambia la costante a occhio.

🟥 SI FERMA INVECE DI INDOVINARE, come lo strumento gemello per la petizione
sanita' Calabria (`aggiorna_firme_petizione.py`): se l'API non risponde, se
cambia formato, o se il numero letto e' assurdo (zero, o piu' del doppio
dell'ultimo valore scritto nell'articolo), il programma non tocca niente.

    python3 _tools/aggiorna_firme_fuori_guerra.py            # aggiorna e pubblica
    python3 _tools/aggiorna_firme_fuori_guerra.py --prova     # dice e basta

⛔ Aggiunge al commit **solo i due file che tocca**, mai `git add -A`.

Nato il 9 settembre 2026 su richiesta di Fernando: lo stesso aggiornamento
costante gia' attivo per la petizione sanita' Calabria, anche per questo
appello. Gira ogni 5 minuti sui server di GitHub (a richiesta di Fernando,
9/09/2026), vedi `.github/workflows/firme-fuori-guerra.yml`.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINA = 'fuori-italia-guerra-mobilitazione-nazionale.html'
HOME = 'index.html'
API = 'https://fuorilitaliadallaguerra.org/api/index.php?limit=1&page=1'
FINTO_BROWSER = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                 '(KHTML, like Gecko) Chrome/126 Safari/537.36')
PRIMI_FIRMATARI = 100  # fisso: vedi nota nel docstring, verificato il 9/09/2026
MESI = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio',
        'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']


def stop(motivo):
    print(f'  ⛔ {motivo} — non tocco niente')
    sys.exit(1)


def sostituisci(testo, schema, nuovo, dove):
    nuovo_testo, quante = re.subn(schema, nuovo, testo, count=1)
    if quante != 1:
        stop(f'{dove}: non trovo piu\' la scritta da cambiare')
    return nuovo_testo


def formato_it(n):
    return f'{n:,}'.replace(',', '.')


def leggi_adesioni():
    richiesta = urllib.request.Request(API, headers={'User-Agent': FINTO_BROWSER})
    try:
        with urllib.request.urlopen(richiesta, timeout=30) as r:
            dati = json.loads(r.read().decode('utf-8'))
    except Exception as e:
        stop(f'l\'API di fuorilitaliadallaguerra.org non risponde ({e})')
    if 'total' not in dati:
        stop('la risposta dell\'API non ha piu\' il campo "total": il sito ha cambiato formato')
    iscritti = int(dati['total'])
    if iscritti <= 0:
        stop(f'numero non credibile: {iscritti} iscritti dal modulo')
    return iscritti + PRIMI_FIRMATARI


def oggi_a_parole():
    d = datetime.now()
    return f'{d.day} {MESI[d.month - 1]} {d.year}'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prova', action='store_true', help='dice cosa farebbe, non scrive')
    a = p.parse_args()

    os.chdir(BASE)
    adesioni = leggi_adesioni()
    print(f'  fuorilitaliadallaguerra.org: {formato_it(adesioni)} adesioni (modulo + primi {PRIMI_FIRMATARI} firmatari)')

    pag = open(PAGINA, encoding='utf-8').read()
    m = re.search(r'<strong>([\d.]+) adesioni</strong>', pag)
    if not m:
        stop('nell\'articolo non trovo piu' + chr(39) + ' «N adesioni»')
    prima = int(m.group(1).replace('.', ''))

    if abs(adesioni - prima) == 0:
        print(f'  = fermo a {formato_it(adesioni)}: niente da cambiare')
        return
    if adesioni < prima or adesioni > prima * 3 + 1000:
        stop(f'salto non credibile: {formato_it(prima)} → {formato_it(adesioni)}')

    testo = sostituisci(pag,
                        r'\(\d{1,2} \w+ \d{4}\) la pagina indica <strong>[\d.]+ adesioni</strong>',
                        f'({oggi_a_parole()}) la pagina indica <strong>{formato_it(adesioni)} adesioni</strong>',
                        'articolo, «la pagina indica N adesioni»')
    testo = sostituisci(testo,
                        r'Adesioni indicate sul sito: <strong style="display:inline">[\d.]+</strong>',
                        f'Adesioni indicate sul sito: <strong style="display:inline">{formato_it(adesioni)}</strong>',
                        'articolo, «Adesioni indicate sul sito»')
    testo = sostituisci(testo, r'(&#x1F4CA; I numeri al )[^<]*',
                        r'\g<1>' + oggi_a_parole(),
                        'articolo, data del riquadro')

    casa = open(HOME, encoding='utf-8').read()
    casa = sostituisci(casa, r'Oltre [\d.]+ adesioni finora',
                       f'Oltre {formato_it(adesioni)} adesioni finora',
                       'home, la card dell\'appello')

    if a.prova:
        print(f'  (prova) {formato_it(prima)} → {formato_it(adesioni)}: non ho scritto niente')
        return

    open(PAGINA, 'w', encoding='utf-8').write(testo)
    open(HOME, 'w', encoding='utf-8').write(casa)
    print(f'  ✅ scritto: {formato_it(prima)} → {formato_it(adesioni)}')

    subprocess.run(['git', 'add', PAGINA, HOME], check=True)
    subprocess.run(['git', 'commit', '-q', '-m',
                    f'Appello "Fuori l\'Italia dalla guerra": {formato_it(adesioni)} adesioni'], check=True)

    # Il cron della petizione Calabria gira ogni 10 minuti, questo ogni 5: ogni
    # due giri su tre cadono nello stesso minuto e possono litigarsi il push
    # (il remoto nel frattempo ha un commit che qui non c'e' ancora). Un solo
    # ritentativo con rebase basta: i due script toccano file diversi (tranne
    # index.html, dove pero' scrivono in punti distinti della card), non c'e'
    # un vero conflitto di contenuto da risolvere a mano.
    esito = subprocess.run(['git', 'push', '-q', 'origin', 'main'])
    if esito.returncode != 0:
        print('  · push respinto (probabile corsa con un altro aggiornamento), riprovo con rebase')
        rb = subprocess.run(['git', 'pull', '--rebase', '-q', 'origin', 'main'])
        if rb.returncode != 0:
            # index.html e' minificato su una riga sola: se la corsa ha toccato
            # quella stessa riga (anche in un punto diverso), il rebase puo'
            # non risolversi da solo. Non si tenta una fusione a mano qui: si
            # abbandona e si lascia perdere questo giro, il prossimo (fra
            # pochi minuti) riparte da capo con i dati freschi.
            subprocess.run(['git', 'rebase', '--abort'])
            stop('corsa con un altro aggiornamento: conflitto sulla home, riprovo al prossimo giro')
        subprocess.run(['git', 'push', '-q', 'origin', 'main'], check=True)
    print('  ✅ pubblicato')


if __name__ == '__main__':
    main()
