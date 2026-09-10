#!/usr/bin/env python3
"""Riallinea le firme delle tre leggi elettorali di Voto LibEguale.

A differenza di quanto documentato per il referendum sull'educazione affettiva
(vedi `aggiorna_firme_referendum.py`), qui la piattaforma del Ministero della
Giustizia **si legge benissimo da fuori**: ogni iniziativa ha un endpoint JSON
pubblico, senza bisogno di browser, cookie o intestazioni speciali:

    https://firmereferendum.giustizia.it/referendum/api-portal/iniziativa/public/<id>

Risponde con `content.sostenitori` (le firme) e `content.quorum` (l'obiettivo,
50.000 per tutte e tre). Trovato il 10/09/2026 guardando le richieste di rete
della pagina — è la stessa chiamata che il sito fa per disegnare la sua barra.
E' la fonte primaria vera, non una scorciatoia: e' l'API del Ministero stesso.

Aggiorna QUATTRO cose per ciascuna delle tre leggi:
  · nell'articolo: il numero e la barra (box "I numeri al ...");
  · nella card fissa in home: il numero e la mini-barra.
E la data del riquadro nell'articolo.

🟥 SI FERMA INVECE DI INDOVINARE: se un endpoint non risponde, se sparisce il
campo atteso, o se il numero letto è assurdo (fuori 0-quorum*2), il programma
non tocca niente per QUELLA legge — ma prova comunque le altre due.

    python3 _tools/aggiorna_firme_voto_libeguale.py            # aggiorna e pubblica
    python3 _tools/aggiorna_firme_voto_libeguale.py --prova     # dice e basta

⛔ Aggiunge al commit solo i due file che tocca, mai `git add -A`.

Nato il 10 settembre 2026 su richiesta di Fernando: le tre barre (nell'articolo
e nella card di home) autoaggiornanti come le altre. Gira ogni 5 minuti sui
server di GitHub, vedi `.github/workflows/firme-voto-libeguale.yml`.
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
PAGINA = 'voto-libeguale-tre-leggi-elettorale.html'
HOME = 'index.html'
FINTO_BROWSER = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                 '(KHTML, like Gecko) Chrome/126 Safari/537.36')
MESI = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio',
        'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']

# id Ministero -> ancore usate nell'articolo e nella card di home
LEGGI = [
    {'id': 5200003, 'art_num': 'vle-num-preferenza', 'art_barra': 'vle-barra-preferenza',
     'card_txt': 'vle-card-preferenza-txt', 'card_barra': 'vle-card-preferenza-barra'},
    {'id': 5200001, 'art_num': 'vle-num-pluricandidature', 'art_barra': 'vle-barra-pluricandidature',
     'card_txt': 'vle-card-pluricandidature-txt', 'card_barra': 'vle-card-pluricandidature-barra'},
    {'id': 5200000, 'art_num': 'vle-num-congiunto', 'art_barra': 'vle-barra-congiunto',
     'card_txt': 'vle-card-congiunto-txt', 'card_barra': 'vle-card-congiunto-barra'},
]


def stop_legge(motivo):
    print(f'  ⛔ {motivo}')


def sostituisci(testo, schema, nuovo, dove):
    nuovo_testo, quante = re.subn(schema, nuovo, testo, count=1)
    if quante != 1:
        print(f'  ⛔ {dove}: non trovo piu\' la scritta da cambiare — non tocco questo punto')
        return testo, False
    return nuovo_testo, True


def sostituisci_nel_marcato(testo, ancora, schema, nuovo, dove):
    marca = 'data-pa-cont="%s"' % ancora
    quante_ancore = testo.count(marca)
    if quante_ancore != 1:
        print(f'  ⛔ {dove}: l\'ancora {ancora} compare {quante_ancore} volte, ne serve 1 — non tocco questo punto')
        return testo, False
    i = testo.index(marca)
    apertura = testo.rfind('<', 0, i)
    nome_tag = re.match(r'<([a-zA-Z0-9]+)', testo[apertura:]).group(1)
    fine_tag = testo.index('>', i) + 1
    chiusura = testo.find('</%s>' % nome_tag, fine_tag)
    fine = chiusura + len(nome_tag) + 3 if chiusura != -1 else fine_tag
    blocco = testo[apertura:fine]
    nuovo_blocco, quante = re.subn(schema, nuovo, blocco, count=1)
    if quante != 1:
        print(f'  ⛔ {dove}: dentro "{ancora}" non trovo la scritta da cambiare — non tocco questo punto')
        return testo, False
    return testo[:apertura] + nuovo_blocco + testo[fine:], True


def formato_it(n):
    return f'{n:,}'.replace(',', '.')


def leggi_sostenitori(id_legge):
    url = f'https://firmereferendum.giustizia.it/referendum/api-portal/iniziativa/public/{id_legge}'
    richiesta = urllib.request.Request(url, headers={'User-Agent': FINTO_BROWSER})
    try:
        with urllib.request.urlopen(richiesta, timeout=20) as r:
            dati = json.loads(r.read().decode('utf-8'))
    except Exception as e:
        stop_legge(f'legge {id_legge}: l\'API del Ministero non risponde ({e})')
        return None, None
    contenuto = dati.get('content') or {}
    sostenitori = contenuto.get('sostenitori')
    quorum = contenuto.get('quorum')
    if sostenitori is None or quorum is None:
        stop_legge(f'legge {id_legge}: la risposta non ha piu\' "sostenitori"/"quorum"')
        return None, None
    if sostenitori < 0 or sostenitori > quorum * 2:
        stop_legge(f'legge {id_legge}: numero non credibile ({sostenitori} su quorum {quorum})')
        return None, None
    return sostenitori, quorum


def oggi_a_parole():
    d = datetime.now()
    return f'{d.day} {MESI[d.month - 1]} {d.year}'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prova', action='store_true', help='dice cosa farebbe, non scrive')
    a = p.parse_args()

    os.chdir(BASE)
    pag = open(PAGINA, encoding='utf-8').read()
    casa = open(HOME, encoding='utf-8').read()

    qualcosa_e_cambiato = False
    almeno_un_ok = False

    for legge in LEGGI:
        sostenitori, quorum = leggi_sostenitori(legge['id'])
        if sostenitori is None:
            continue
        pct = round(sostenitori / quorum * 100, 1)
        formattato = formato_it(sostenitori)
        print(f'  legge {legge["id"]}: {formattato} / {formato_it(quorum)} ({pct}%)')

        pag, ok1 = sostituisci_nel_marcato(pag, legge['art_num'],
                            r'[\d.]+ / [\d.]+ \([\d.]+%\)',
                            f'{formattato} / {formato_it(quorum)} ({pct}%)',
                            f'articolo, legge {legge["id"]}: numero')
        pag, ok2 = sostituisci_nel_marcato(pag, legge['art_barra'],
                            r'width:[\d.]+%',
                            f'width:{pct}%',
                            f'articolo, legge {legge["id"]}: barra')
        casa, ok3 = sostituisci_nel_marcato(casa, legge['card_txt'],
                            r'[\d.]+%',
                            f'{pct}%',
                            f'home, legge {legge["id"]}: numero card')
        casa, ok4 = sostituisci_nel_marcato(casa, legge['card_barra'],
                            r'width:[\d.]+%',
                            f'width:{pct}%',
                            f'home, legge {legge["id"]}: barra card')

        if ok1 or ok2 or ok3 or ok4:
            qualcosa_e_cambiato = True
        if ok1 and ok2 and ok3 and ok4:
            almeno_un_ok = True

    if not qualcosa_e_cambiato:
        print('  = nessuna modifica da fare')
        return

    if almeno_un_ok:
        pag, _ = sostituisci(pag, r'(&#x1F4CA; I numeri al )[^<]*',
                             r'\g<1>' + oggi_a_parole(),
                             'articolo, data del riquadro')

    if a.prova:
        print('  (prova) non ho scritto niente')
        return

    open(PAGINA, 'w', encoding='utf-8').write(pag)
    open(HOME, 'w', encoding='utf-8').write(casa)
    print('  ✅ scritto')

    subprocess.run(['git', 'add', PAGINA, HOME], check=True)
    subprocess.run(['git', 'commit', '-q', '-m', 'Voto LibEguale: aggiornate le firme delle tre leggi'], check=True)

    esito = subprocess.run(['git', 'push', '-q', 'origin', 'main'])
    if esito.returncode != 0:
        print('  · push respinto (probabile corsa con un altro aggiornamento), riprovo con rebase')
        rb = subprocess.run(['git', 'pull', '--rebase', '-q', 'origin', 'main'])
        if rb.returncode != 0:
            subprocess.run(['git', 'rebase', '--abort'])
            print('  ⛔ corsa con un altro aggiornamento: conflitto sulla home, riprovo al prossimo giro')
            sys.exit(1)
        subprocess.run(['git', 'push', '-q', 'origin', 'main'], check=True)
    print('  ✅ pubblicato')


if __name__ == '__main__':
    main()
