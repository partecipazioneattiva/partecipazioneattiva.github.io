#!/usr/bin/env python3
"""Riallinea il contatore delle firme della petizione sulla sanita' in Calabria.

Legge il numero vero da Change.org e lo riscrive in sei posti:
  · nell'articolo: «Firme raccolte», «Obiettivo dichiarato», «Mancano N firme»
    e la data del riquadro «I numeri al ...»;
  · nella home: la scritta «N firme su N», il titolo della card («arrivare a N
    firme») e la larghezza della barra.

⚠️ Il traguardo **si muove da solo**: quando la petizione supera l'obiettivo,
Change.org lo raddoppia senza avvisare (il 25 agosto 2026: da 500 a 1000). Per
questo nessuno dei sei punti e' scritto a mano nel programma — si cerca il
numero che c'e' e si sostituisce quello, qualunque sia.

Poi committa e pubblica **solo se qualcosa e' cambiato davvero**. Gira da solo
**ogni 10 minuti sui server di GitHub**, quindi anche a Mac spento, e non consuma
crediti: lo chiama `.github/workflows/firme-petizione.yml`.

    python3 _tools/aggiorna_firme_petizione.py            # aggiorna e pubblica
    python3 _tools/aggiorna_firme_petizione.py --prova     # dice e basta

🟥 SI FERMA INVECE DI INDOVINARE. Se Change.org non risponde, se cambia il modo
in cui scrive il contatore, se il numero e' assurdo (zero, o piu' del doppio
dell'obiettivo) o se una delle scritte da sostituire non si trova piu' nel sito,
il programma **non tocca niente** ed esce con un messaggio. Un contatore fermo
si nota; un contatore sbagliato no.

⛔ Aggiunge al commit **solo i due file che tocca**, mai `git add -A`: il
repository e' pubblico (regola in CLAUDE.md, e c'e' la guardia che blocca).

🟨 Non rigenera l'indice della ricerca: chi cerca «firme» dentro il sito vede il
numero dell'ultima ricostruzione, non l'ultimo. E' una differenza di poche
unita' e non vale il costo di ricostruire Pagefind a ogni giro.

Nato il 12 agosto 2026, su richiesta di Fernando: «riesci a darti tipo un timer
ogni 12 ore per aggiornare il numero». Il 14 agosto 2026, alla domanda «si puo'
fare in tempo reale?», il lavoro e' passato **dal Mac a GitHub**: prima ogni due
ore col Mac acceso, ora ogni 10 minuti sempre. Piu' vicino di cosi' non si va:
Change.org non ha ne' un riquadro da incorporare ne' un indirizzo leggibile dal
browser, quindi il numero va per forza riscritto dentro l'HTML.

--------------------------------------------------------------------------
CHI LO FA PARTIRE

  .github/workflows/firme-petizione.yml   ogni 10 minuti + a mano da Actions

Il cron di GitHub puo' ritardare di qualche minuto nelle ore di punta: il numero
al massimo invecchia, non sbaglia.

`--installa` scrive ancora il .plist per launchd (`it.pa.firme-petizione`), ma
serve solo come ripiego se GitHub Actions venisse spento. ⚠️ Non tenere accesi
tutti e due: si accavallano sullo stesso push. Il .plist si toglie con

  launchctl bootout gui/$UID/it.pa.firme-petizione
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
PAGINA = 'sanita-calabria-petizione-comunita-competente.html'
HOME = 'index.html'
INDIRIZZO = 'https://www.change.org/p/per-una-compiuta-riforma-della-sanit%C3%A0-in-calabria'
FINTO_BROWSER = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                 '(KHTML, like Gecko) Chrome/126 Safari/537.36')
MESI = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio',
        'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']
ETICHETTA = 'it.pa.firme-petizione'


def stop(motivo):
    print(f'  ⛔ {motivo} — non tocco niente')
    sys.exit(1)


def sostituisci(testo, schema, nuovo, dove):
    """Sostituisce una volta sola, e si ferma se non ha trovato niente.

    Un `.replace()` andato a vuoto non protesta: lascia il numero vecchio e il
    programma dice lo stesso «fatto». E' cosi' che il 25 agosto 2026 la frase
    «Mancano 35 firme» sarebbe rimasta sbagliata in silenzio. Qui un buco vale
    uno stop, come tutto il resto del programma.
    """
    nuovo_testo, quante = re.subn(schema, nuovo, testo, count=1)
    if quante != 1:
        stop(f'{dove}: non trovo piu\' la scritta da cambiare')
    return nuovo_testo


def leggi_contatore():
    richiesta = urllib.request.Request(INDIRIZZO, headers={'User-Agent': FINTO_BROWSER})
    try:
        with urllib.request.urlopen(richiesta, timeout=30) as r:
            pagina = r.read().decode('utf-8', 'replace')
    except Exception as e:
        stop(f'Change.org non risponde ({e})')

    m = re.search(r'"signatureCount":\{"displayed":(\d+),"total":(\d+),"goal":(\d+)\}', pagina)
    if not m:
        stop('il contatore non si legge piu\': Change.org ha cambiato la pagina')
    firme, obiettivo = int(m.group(2)), int(m.group(3))
    if firme <= 0 or firme > obiettivo * 2:
        stop(f'numero non credibile: {firme} firme su {obiettivo}')
    return firme, obiettivo


def oggi_a_parole():
    d = datetime.now()
    return f'{d.day} {MESI[d.month - 1]} {d.year}'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prova', action='store_true', help='dice cosa farebbe, non scrive')
    p.add_argument('--installa', action='store_true', help='scrive il .plist per launchd')
    a = p.parse_args()

    if a.installa:
        installa()
        return

    os.chdir(BASE)
    firme, obiettivo = leggi_contatore()
    quota = round(firme / obiettivo * 100, 1)
    print(f'  Change.org dice: {firme} firme su {obiettivo} ({quota}%)')

    pag = open(PAGINA, encoding='utf-8').read()
    m = re.search(r'Firme raccolte: <strong style="display:inline">(\d+)</strong>', pag)
    if not m:
        stop('nella pagina non trovo piu\' «Firme raccolte»')
    prima = int(m.group(1))
    m = re.search(r'Obiettivo dichiarato: <strong style="display:inline">(\d+)</strong>', pag)
    if not m:
        stop('nella pagina non trovo piu\' «Obiettivo dichiarato»')
    traguardo_prima = int(m.group(1))

    if prima == firme and traguardo_prima == obiettivo:
        print(f'  = fermo a {firme} su {obiettivo}: niente da cambiare')
        return
    if traguardo_prima != obiettivo:
        print(f'  ⚠️  Change.org ha spostato il traguardo: {traguardo_prima} → {obiettivo}')

    testo = sostituisci(pag,
                        r'Firme raccolte: <strong style="display:inline">\d+</strong>',
                        f'Firme raccolte: <strong style="display:inline">{firme}</strong>',
                        'articolo, «Firme raccolte»')
    testo = sostituisci(testo,
                        r'Obiettivo dichiarato: <strong style="display:inline">\d+</strong>',
                        f'Obiettivo dichiarato: <strong style="display:inline">{obiettivo}</strong>',
                        'articolo, «Obiettivo dichiarato»')
    testo = sostituisci(testo, r'Mancano \d+ firme',
                        f'Mancano {obiettivo - firme} firme',
                        'articolo, «Mancano N firme»')
    testo = sostituisci(testo, r'(&#x1F4CA; I numeri al )[^<]*',
                        r'\g<1>' + oggi_a_parole(),
                        'articolo, data del riquadro')

    casa = open(HOME, encoding='utf-8').read()
    casa = sostituisci(casa, r'\d+ firme su \d+',
                       f'{firme} firme su {obiettivo}',
                       'home, la scritta delle firme')
    casa = sostituisci(casa, r'(arrivare a )\d+( firme)',
                       r'\g<1>' + str(obiettivo) + r'\g<2>',
                       'home, il titolo della card')
    casa = sostituisci(casa,
                       r'(background:rgba\(255,255,255,\.22\)[^"]*"><span style="display:block;'
                       r'height:100%;width:)[\d.]+%',
                       r'\g<1>' + f'{quota}%',
                       'home, la barra di avanzamento')

    if a.prova:
        print(f'  (prova) {prima} → {firme}, barra al {quota}%: non ho scritto niente')
        return

    open(PAGINA, 'w', encoding='utf-8').write(testo)
    open(HOME, 'w', encoding='utf-8').write(casa)
    print(f'  ✅ scritto: {prima} → {firme}')

    subprocess.run(['git', 'add', PAGINA, HOME], check=True)
    messaggio = f'La petizione sulla sanita\' in Calabria e\' a {firme} firme'
    if traguardo_prima != obiettivo:
        messaggio += f' (traguardo spostato da {traguardo_prima} a {obiettivo})'
    subprocess.run(['git', 'commit', '-q', '-m', messaggio], check=True)
    subprocess.run(['git', 'push', '-q', 'origin', 'main'], check=True)
    print('  ✅ pubblicato')


def installa():
    plist = os.path.expanduser(f'~/Library/LaunchAgents/{ETICHETTA}.plist')
    log = os.path.expanduser('~/Library/Logs/pa-firme-petizione.log')
    contenuto = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>{ETICHETTA}</string>
  <key>ProgramArguments</key><array>
    <string>{sys.executable}</string>
    <string>{os.path.abspath(__file__)}</string>
  </array>
  <key>StartInterval</key><integer>3600</integer>
  <key>RunAtLoad</key><false/>
  <key>StandardOutPath</key><string>{log}</string>
  <key>StandardErrorPath</key><string>{log}</string>
</dict></plist>
'''
    open(plist, 'w', encoding='utf-8').write(contenuto)
    print(f'  scritto {plist}')
    print(f'  ora: launchctl bootstrap gui/$UID {plist}')
    print(f'  il diario finisce in {log}')


if __name__ == '__main__':
    main()
