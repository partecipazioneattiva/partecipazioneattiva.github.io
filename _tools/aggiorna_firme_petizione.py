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
    casa = sostituisci_nel_marcato(casa, 'calabria-firme', r'\d+ firme su \d+',
                       f'{firme} firme su {obiettivo}',
                       'home, la scritta delle firme')
    # Il 03/09/2026 il titolo della card e' passato da «aiutiamo Comunita'
    # Competente ad arrivare a 1000 firme» a «Sanita' in Calabria: firmiamo»:
    # l'obiettivo li' non c'e' piu', e nella home resta solo dentro «N firme su
    # N», che si aggiorna qui sopra. Percio' facoltativa — se il titolo tornera'
    # a nominarlo, riprende da sola.
    casa = sostituisci(casa, r'(arrivare a )\d+( firme)',
                       r'\g<1>' + str(obiettivo) + r'\g<2>',
                       'home, il titolo della card', facoltativo=True)
    casa = sostituisci_nel_marcato(casa, 'calabria-barra',
                       r'(width:)[\d.]+%',
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

    # Dal 9/09/2026 anche l'appello "Fuori l'Italia dalla guerra" ha un cron
    # gemello (ogni 5 minuti) che tocca la stessa index.html: un push respinto
    # per corsa non e' piu' un caso raro. index.html e' minificata su una riga
    # sola, quindi un rebase puo' non risolversi da solo se la corsa ha toccato
    # la stessa riga: in quel caso si abbandona e si lascia perdere questo
    # giro, il prossimo (fra dieci minuti) riparte da capo.
    esito = subprocess.run(['git', 'push', '-q', 'origin', 'main'])
    if esito.returncode != 0:
        print('  · push respinto (probabile corsa con un altro aggiornamento), riprovo con rebase')
        rb = subprocess.run(['git', 'pull', '--rebase', '-q', 'origin', 'main'])
        if rb.returncode != 0:
            subprocess.run(['git', 'rebase', '--abort'])
            stop('corsa con un altro aggiornamento: conflitto sulla home, riprovo al prossimo giro')
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
