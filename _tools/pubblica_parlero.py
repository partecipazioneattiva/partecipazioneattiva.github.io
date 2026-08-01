#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pubblica le puntate del podcast "Parlero" sul sito.

    python3 _tools/pubblica_parlero.py            # prova, non scrive
    python3 _tools/pubblica_parlero.py --applica  # scrive davvero

Fonte di verita': `parlero_puntate.json`. Da li' questo script rigenera
DUE cose, e nessuna delle due si tocca a mano:

  1. la sezione podcast dentro `parlero.html`, fra i marcatori
     <!--PARLERO-PODCAST-INIZIO--> e <!--PARLERO-PODCAST-FINE-->;
  2. `podcast.xml`, il feed RSS con i tag iTunes che Apple Podcasts e
     Spotify pretendono (il `feed.xml` del sito e' un'altra cosa: e'
     l'RSS degli articoli, e `parlero.html` sta perfino nella sua lista
     di esclusioni).

⛔ DUE BLOCCHI NON NEGOZIABILI, e sono di legge, non di stile:

  - **`approvato`**: ogni puntata deve dire come e quando Antonio
    Cristiano ha approvato il testo. La voce e' clonata da una persona
    reale (manuale di compliance §2) e qui non legge notizie, dice
    opinioni: senza il suo ok scritto la puntata non esce. Manca il
    campo → lo script si ferma.
  - **dicitura IA**: art. 50 AI Act, in vigore dal 2 agosto 2026. La
    riga sulla voce sintetica viene scritta da qui sia nella pagina sia
    in ogni item del feed. Non e' un parametro: non si puo' spegnere.

Il volto animato resta fuori: l'autorizzazione copre la voce, non
l'immagine. Qui infatti si pubblica solo audio.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from email.utils import format_datetime
from html import escape
from xml.sax.saxutils import escape as xesc
from zoneinfo import ZoneInfo

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(BASE, 'parlero_puntate.json')
PAGINA = os.path.join(BASE, 'parlero.html')
WEBTV = os.path.join(BASE, 'webtv.html')
FEED = os.path.join(BASE, 'podcast.xml')

DOMINIO = 'https://partecipazione-attiva.it'
COPERTINA = f'{DOMINIO}/images/parlero-podcast-cover.jpg'
POSTA = 'webmaster.partecipazione.attiva@gmail.com'
ROMA = ZoneInfo('Europe/Rome')

INIZIO = '<!--PARLERO-PODCAST-INIZIO-->'
FINE = '<!--PARLERO-PODCAST-FINE-->'

# Gli stessi marcatori, dentro la sezione Parlero di webtv.html.
# Parlero e' un programma di **Partecipazione Attiva WebTV** — TV Flegrea
# viene dopo (deciso da Fernando, 01/08/2026) — quindi l'ultima puntata si
# annuncia anche li', e non a mano.
W_INIZIO = '<!--PARLERO-PODCAST-WEBTV-INIZIO-->'
W_FINE = '<!--PARLERO-PODCAST-WEBTV-FINE-->'
W_ANCORA = re.compile(
    r'(<div class="tv-section" id="parlero">\s*<div class="tv-section-head">'
    r'.*?</div>)', re.S)

# Il punto della pagina dove la sezione si innesta la prima volta: subito
# prima del blocco "dove si vede e si ascolta".
# ⚠️ Ci si aggancia alla CLASSE, non al testo dell'h2. Il 01/08/2026 quel
# titolo e' cambiato ("In onda su TV Flegrea" → "Dove si vede e si ascolta")
# e lo script, che cercava le parole, si e' fermato.
ANCORA = re.compile(r'<section class=tv-section>')

DICITURA = ('La voce di questa puntata è generata con intelligenza '
            'artificiale a partire dalla voce di Antonio Cristiano, che ne '
            'ha autorizzato l’uso e approva il testo di ogni puntata prima '
            'della pubblicazione.')

MESI = ('gennaio febbraio marzo aprile maggio giugno luglio agosto '
        'settembre ottobre novembre dicembre').split()


def stop(messaggio):
    sys.exit(f'⛔ STOP: {messaggio}')


def durata_e_peso(percorso_assoluto):
    """(secondi, byte) di un mp3. La durata la misura ffprobe."""
    byte = os.path.getsize(percorso_assoluto)
    try:
        out = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', percorso_assoluto],
            capture_output=True, text=True, check=True).stdout.strip()
        return int(round(float(out))), byte
    except Exception as e:
        stop(f'ffprobe non ha letto la durata di {percorso_assoluto}: {e}')


def mmss(secondi):
    return f'{secondi // 60}:{secondi % 60:02d}'


def data_lunga(d):
    return f'{d.day} {MESI[d.month - 1]} {d.year}'


def carica():
    with open(DATI, encoding='utf-8') as f:
        dati = json.load(f)

    puntate = dati.get('puntate', [])
    if not puntate:
        print('Nessuna puntata in parlero_puntate.json: non c\'e\' niente da '
              'pubblicare.')
        return []

    for p in puntate:
        for campo in ('n', 'titolo', 'data', 'descrizione', 'audio'):
            if not p.get(campo):
                stop(f'puntata {p.get("n", "?")}: manca il campo "{campo}"')

        # "reale" = l'ha registrata Antonio con la sua voce; "sintetica" =
        # generata con la pipeline del TG. Cambia due cose: la dicitura IA
        # (obbligatoria solo sulla sintetica) e il blocco qui sotto.
        p['_sintetica'] = p.get('voce', 'sintetica') != 'reale'

        # ⛔ Il blocco di compliance: nessuna approvazione, nessuna puntata.
        # Sulla voce reale non serve: registrando, ha approvato.
        if p['_sintetica'] and not p.get('approvato'):
            stop(f'puntata {p["n"]} ("{p["titolo"]}"): manca "approvato".\n'
                 f'   La voce e\' quella di una persona reale e qui dice '
                 f'opinioni.\n'
                 f'   Serve l\'ok scritto di Antonio Cristiano sul testo, '
                 f'annotato\n'
                 f'   nel campo "approvato" (es. "WhatsApp 2026-08-05").')

        percorso = os.path.join(BASE, p['audio'])
        if not os.path.exists(percorso):
            stop(f'puntata {p["n"]}: l\'audio {p["audio"]} non esiste')

        p['_secondi'], p['_byte'] = durata_e_peso(percorso)
        p['_data'] = datetime.strptime(p['data'], '%Y-%m-%d').replace(
            hour=12, tzinfo=ROMA)

    puntate.sort(key=lambda p: p['n'], reverse=True)
    return puntate


def sezione_html(puntate):
    """La sezione podcast della pagina, dai marcatori compresi."""
    card = []
    for p in puntate:
        card.append(f'''
    <article class=pod-card>
      <div class=pod-testa>
        <span class=pod-num>Puntata {p["n"]}</span>
        <span class=pod-data>{data_lunga(p["_data"])} &middot; {mmss(p["_secondi"])}</span>
      </div>
      <h3>{escape(p["titolo"])}</h3>
      <p>{escape(p["descrizione"])}</p>
      <audio controls preload=none src="{p["audio"]}">
        Il tuo browser non riproduce l&rsquo;audio:
        <a href="{p["audio"]}">scarica la puntata</a>.
      </audio>{'''
      <p class=pod-ia-card>&#9432; ''' + escape(DICITURA) + '</p>' if p['_sintetica'] else ''}
    </article>''')

    return f'''{INIZIO}
<section class=pod-section id=podcast>
  <div class=pod-head>
    <h2>Parler&ograve; &mdash; il podcast</h2>
    <p class=pod-occhiello>Il commento di Antonio Cristiano. Una puntata a
    settimana: un fatto di Napoli o d&rsquo;Italia, e cosa ci dice davvero.</p>
    <a class=pod-feed href="podcast.xml">
      Ascolta nella tua app: copia questo indirizzo &rarr; {DOMINIO}/podcast.xml
    </a>
  </div>
  <div class=pod-lista>{''.join(card)}
  </div>
</section>
{FINE}'''


CSS = '''
/* --- podcast Parlero (generato da _tools/pubblica_parlero.py) --- */
.pod-section{max-width:820px;margin:0 auto;padding:54px 20px}
.pod-head h2{font-family:montserrat,sans-serif;color:#8a4e00;font-size:1.9em;margin-bottom:10px}
.pod-occhiello{color:#444;margin-bottom:14px}
.pod-feed{display:inline-block;font-size:.82em;color:#8a4e00;text-decoration:none;border:1.5px solid #e8900a;border-radius:8px;padding:8px 14px;word-break:break-all}
.pod-feed:hover{background:#fff8ee}
.pod-ia-card{font-size:.76em!important;color:#5a4632;background:#fff8ee;border-left:4px solid #e8900a;border-radius:0 8px 8px 0;padding:10px 12px;margin:14px 0 0!important}
.pod-card{background:#fff;border:1px solid #ecdcc4;border-radius:14px;padding:22px;margin-bottom:18px;box-shadow:0 2px 12px rgba(0,0,0,.05)}
.pod-testa{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:8px}
.pod-num{font-family:montserrat,sans-serif;font-weight:700;font-size:.76em;letter-spacing:.08em;text-transform:uppercase;color:#e8900a}
.pod-data{font-size:.78em;color:#777}
.pod-card h3{font-family:montserrat,sans-serif;color:#8a4e00;font-size:1.18em;margin-bottom:8px}
.pod-card p{color:#444;font-size:.95em;margin-bottom:14px}
.pod-card audio{width:100%}
'''


def scrivi_pagina(puntate, applica):
    with open(PAGINA, encoding='utf-8') as f:
        html = f.read()

    nuova = sezione_html(puntate)

    if INIZIO in html:
        i = html.index(INIZIO)
        j = html.index(FINE) + len(FINE)
        html = html[:i] + nuova + html[j:]
        dove = 'sezione rigenerata'
    else:
        m = ANCORA.search(html)
        if not m:
            stop('non trovo dove innestare la sezione in parlero.html '
                 '(cercavo <section class=tv-section>)')
        html = html[:m.start()] + nuova + '\n' + html[m.start():]
        dove = 'sezione inserita per la prima volta'

    if '.pod-section{' not in html:
        k = html.index('</style>')
        html = html[:k] + CSS + html[k:]
        dove += ' + CSS aggiunto'

    if applica:
        with open(PAGINA, 'w', encoding='utf-8') as f:
            f.write(html)
    print(f'  parlero.html — {dove}')


def scrivi_webtv(puntate, applica):
    """Il richiamo all'ultima puntata dentro la sezione Parlero di webtv.html."""
    with open(WEBTV, encoding='utf-8') as f:
        html = f.read()

    u = puntate[0]
    blocco = (
        f'{W_INIZIO}\n'
        f'    <p class="tv-nota-ia" style="background:#fff8ee;border-left:4px '
        f'solid #e8900a">&#127911; <strong>Il podcast</strong> &mdash; ultima '
        f'puntata: &laquo;{escape(u["titolo"])}&raquo; ({data_lunga(u["_data"])}, '
        f'{mmss(u["_secondi"])}). '
        f'<a href="parlero.html#podcast">Ascolta tutte le puntate</a>.</p>\n'
        f'    {W_FINE}')

    if W_INIZIO in html:
        i = html.index(W_INIZIO)
        j = html.index(W_FINE) + len(W_FINE)
        html = html[:i] + blocco + html[j:]
        dove = 'richiamo aggiornato'
    else:
        m = W_ANCORA.search(html)
        if not m:
            stop('non trovo la sezione id="parlero" in webtv.html')
        html = html[:m.end()] + '\n    ' + blocco + html[m.end():]
        dove = 'richiamo inserito'

    if applica:
        with open(WEBTV, 'w', encoding='utf-8') as f:
            f.write(html)
    print(f'  webtv.html — {dove}')


def scrivi_feed(puntate, applica):
    item = []
    for p in puntate:
        url = f'{DOMINIO}/{p["audio"]}'
        testo = f'{p["descrizione"]}\n\n{DICITURA}'
        item.append(f'''  <item>
    <title>{xesc(p["titolo"])}</title>
    <link>{DOMINIO}/parlero.html#podcast</link>
    <guid isPermaLink="false">parlero-{p["n"]:03d}</guid>
    <pubDate>{format_datetime(p["_data"])}</pubDate>
    <description>{xesc(testo)}</description>
    <enclosure url="{xesc(url)}" length="{p["_byte"]}" type="audio/mpeg"/>
    <itunes:episode>{p["n"]}</itunes:episode>
    <itunes:duration>{p["_secondi"]}</itunes:duration>
    <itunes:summary>{xesc(testo)}</itunes:summary>
    <itunes:explicit>false</itunes:explicit>
  </item>''')

    ultima = puntate[0]['_data'] if puntate else datetime.now(ROMA)
    feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generato da _tools/pubblica_parlero.py — non modificare a mano. -->
<rss version="2.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Parler&#242; — il commento di Antonio Cristiano</title>
    <link>{DOMINIO}/parlero.html</link>
    <description>Napoli, e quello che da Napoli si vede. Una puntata a settimana: un fatto di cronaca o di politica, e il commento che nel telegiornale non ci sta. {xesc(DICITURA)}</description>
    <language>it</language>
    <copyright>Partecipazione Attiva</copyright>
    <atom:link href="{DOMINIO}/podcast.xml" rel="self" type="application/rss+xml"/>
    <lastBuildDate>{format_datetime(ultima)}</lastBuildDate>
    <itunes:author>Partecipazione Attiva</itunes:author>
    <itunes:owner>
      <itunes:name>Partecipazione Attiva</itunes:name>
      <itunes:email>{POSTA}</itunes:email>
    </itunes:owner>
    <itunes:image href="{COPERTINA}"/>
    <itunes:category text="News">
      <itunes:category text="Politics"/>
    </itunes:category>
    <itunes:category text="Society &amp; Culture"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:type>episodic</itunes:type>
{chr(10).join(item)}
  </channel>
</rss>
'''
    if applica:
        with open(FEED, 'w', encoding='utf-8') as f:
            f.write(feed)
    print(f'  podcast.xml — {len(puntate)} puntate')


def main():
    applica = '--applica' in sys.argv
    puntate = carica()
    if not puntate:
        return 0

    print(f'{"SCRIVO" if applica else "PROVA (niente --applica)"}: '
          f'{len(puntate)} puntate')
    scrivi_pagina(puntate, applica)
    scrivi_webtv(puntate, applica)
    scrivi_feed(puntate, applica)

    if applica:
        print('\n✅ Fatto. Resta fuori da questo script, e va fatto a mano:')
        print('   • la voce nel ticker della home (novita.json + '
              'aggiorna_ticker.py)')
    else:
        print('\n(prova: non ho scritto niente. Rilancia con --applica)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
