#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AGGIORNA IL CONTATORE DEL REFERENDUM SULL'EDUCAZIONE AFFETTIVA.

Dove prende il numero (10/09/2026): la piattaforma del Ministero della
Giustizia **non si legge da fuori** — e' tutta JavaScript e le sue API
rispondono 403. Il contatore vero lo pubblica il **comitato promotore**, che
lo espone su un indirizzo che risponde anche a uno script:

    https://referendumeducazioneaffettiva.it/wp-admin/admin-ajax.php?action=get_firme_live

Risponde 7 byte, il numero e basta: `525.374`. E' l'indirizzo che alimenta il
contatore sul loro sito (`<span id="firme-referendum-live">`), trovato
guardando le richieste di rete della pagina.

⚠️ Non e' la fonte primaria ma la piu' vicina che sia leggibile: il numero e'
del comitato, non del Ministero. Percio' in pagina si scrive che sono le firme
dichiarate dal comitato promotore.

🟩 L'obiettivo (500.000) e' gia' stato superato: la barra resta piena e il testo
dice «obiettivo raggiunto». Si continua a firmare perche' la raccolta e' aperta
fino a fine settembre e una parte delle firme viene scartata nei controlli.
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
def stop(motivo):
    print(f'  ⛔ {motivo} — non tocco niente')
    sys.exit(1)


def sostituisci(testo, schema, nuovo, dove, facoltativo=False):
    """Sostituisce una volta sola, e si ferma se non ha trovato niente.

    Un `.replace()` andato a vuoto non protesta: lascia il numero vecchio e il
    programma dice lo stesso «fatto». E' cosi' che il 25 agosto 2026 la frase
    «Mancano 35 firme» sarebbe rimasta sbagliata in silenzio. Qui un buco vale
    uno stop, come tutto il resto del programma.

    `facoltativo=True` serve al caso opposto: un punto dove il numero **puo'
    legittimamente non esserci piu'**, perche' il testo intorno e' stato
    riscritto. Li' un buco non e' un numero vecchio rimasto in giro, e fermarsi
    bloccherebbe anche gli aggiornamenti che invece si possono fare.
    Si usa solo dove si e' verificato che quel numero non compare piu' da nessuna
    parte: se compare, la sostituzione resta obbligatoria.
    """
    nuovo_testo, quante = re.subn(schema, nuovo, testo, count=1)
    if quante != 1:
        if facoltativo:
            print(f'  · {dove}: la scritta non c\'e\' piu\', tiro dritto')
            return testo
        stop(f'{dove}: non trovo piu\' la scritta da cambiare')
    return nuovo_testo


def sostituisci_nel_marcato(testo, ancora, schema, nuovo, dove):
    """Sostituisce SOLO dentro l'elemento marcato con data-pa-cont="ancora".

    Perche' esiste (10/09/2026). Prima si cercava la scritta da cambiare in
    tutta la pagina, con count=1: si prendeva la PRIMA che capitava. Ma la
    barra della Calabria e quella dell'appello sulla guerra sono scritte in
    modo identico, e la prima in pagina era quella sbagliata: il contatore
    della Calabria stava aggiornando la barra dell'appello. Nessun errore,
    nessun avviso — solo un numero fermo (barra al 65,2% con 653 firme).

    E' la trappola che gli esperti chiamano *fragile pattern matching*:
    agganciare uno script a una frase, che chi scrive gli articoli puo'
    riscrivere in qualunque momento senza sapere che qualcosa ci si appoggia.
    E' gia' successo il 03/09/2026 col titolo della card.

    La cura raccomandata e' un identificatore messo apposta nell'HTML —
    `data-pa-cont="..."` — che e' **univoco per costruzione** e non dipende dal
    testo intorno. Qui l'unicita' non si presume: si verifica a ogni giro, e se
    l'ancora manca o e' doppia il programma si ferma invece di indovinare.

    ⛔ Se sposti o riscrivi una card, l'attributo data-pa-cont va con lei.
    """
    marca = 'data-pa-cont="%s"' % ancora
    quante_ancore = testo.count(marca)
    if quante_ancore != 1:
        stop('%s: l\'ancora %s compare %d volte nella pagina, ne serve esattamente 1'
             % (dove, ancora, quante_ancore))
    i = testo.index(marca)
    apertura = testo.rfind('<', 0, i)
    nome_tag = re.match(r'<([a-zA-Z0-9]+)', testo[apertura:]).group(1)
    fine_tag = testo.index('>', i) + 1
    chiusura = testo.find('</%s>' % nome_tag, fine_tag)
    fine = chiusura + len(nome_tag) + 3 if chiusura != -1 else fine_tag
    blocco = testo[apertura:fine]
    nuovo_blocco, quante = re.subn(schema, nuovo, blocco, count=1)
    if quante != 1:
        stop('%s: dentro l\'elemento marcato "%s" non trovo la scritta da cambiare'
             % (dove, ancora))
    return testo[:apertura] + nuovo_blocco + testo[fine:]





PAGINA = 'referendum-educazione-affettiva-scuole.html'
HOME = 'index.html'
API = ('https://referendumeducazioneaffettiva.it/wp-admin/admin-ajax.php'
       '?action=get_firme_live&nocache=')
OBIETTIVO = 500000
FINTO_BROWSER = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                 '(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36')


def formato_it(n):
    return f'{n:,}'.replace(',', '.')


def leggi_firme():
    import time
    richiesta = urllib.request.Request(API + str(int(time.time())),
                                       headers={'User-Agent': FINTO_BROWSER})
    try:
        with urllib.request.urlopen(richiesta, timeout=30) as r:
            grezzo = r.read().decode('utf-8', 'replace').strip()
    except Exception as e:
        stop(f'non riesco a leggere il contatore del comitato: {e}')
    m = re.search(r'([\d.]{5,10})', grezzo)
    if not m:
        stop(f'il contatore ha risposto qualcosa che non e\' un numero: {grezzo[:80]!r}')
    firme = int(m.group(1).replace('.', ''))
    if not (100000 <= firme <= 5000000):
        stop(f'numero fuori scala: {firme}. Non tocco niente.')
    return firme


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--prova', action='store_true', help='non scrive niente')
    a = a.parse_args()

    firme = leggi_firme()
    quota = min(100.0, round(firme / OBIETTIVO * 100, 1))
    raggiunto = firme >= OBIETTIVO
    print(f'  il comitato dice: {formato_it(firme)} firme su {formato_it(OBIETTIVO)} '
          f'({quota}%){" - obiettivo raggiunto" if raggiunto else ""}')

    casa = open(HOME, encoding='utf-8').read()
    prima = re.search(r'data-pa-cont="referendum-firme"[^>]*>([\d.]+)', casa)
    prima = prima.group(1) if prima else '?'
    if prima.replace('.', '') == str(firme):
        print(f'  = fermo a {formato_it(firme)}: niente da cambiare')
        return

    testo_nuovo = (f'{formato_it(firme)} firme &mdash; obiettivo raggiunto' if raggiunto
                   else f'{formato_it(firme)} firme su {formato_it(OBIETTIVO)}')
    casa = sostituisci_nel_marcato(casa, 'referendum-firme',
                                   r'[\d.]+ firme[^<]*', testo_nuovo,
                                   'home, il contatore del referendum')
    casa = sostituisci_nel_marcato(casa, 'referendum-barra',
                                   r'(width:)[\d.]+%', r'\g<1>' + f'{quota}%',
                                   'home, la barra del referendum')

    if a.prova:
        print(f'  (prova) {prima} -> {formato_it(firme)}: non ho scritto niente')
        return

    open(HOME, 'w', encoding='utf-8').write(casa)
    print(f'  OK scritto: {prima} -> {formato_it(firme)}')

    subprocess.run(['git', 'add', HOME], check=True)
    subprocess.run(['git', 'commit', '-q', '-m',
                    f'Referendum educazione affettiva: {formato_it(firme)} firme'], check=True)
    # gli altri due contatori toccano la stessa index.html: un push respinto
    # non e' un guasto, si riprova dopo aver riallineato
    for tentativo in range(3):
        if subprocess.run(['git', 'push']).returncode == 0:
            print('  OK pubblicato')
            return
        print(f'  push respinto (tentativo {tentativo+1}/3): riallineo e riprovo')
        subprocess.run(['git', 'pull', '--no-rebase', '--no-edit'], check=False)
    stop('push respinto tre volte: guarda a mano')


if __name__ == '__main__':
    main()
