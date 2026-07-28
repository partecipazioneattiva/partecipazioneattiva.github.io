#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Riscrive la card 'ultima uscita' in cima alla home da novita.json.

USO
    python3 _tools/aggiorna_novita.py             # anteprima, non scrive
    python3 _tools/aggiorna_novita.py --applica   # scrive index.html

PERCHE' ESISTE
--------------
Fino al 28/07/2026 la home non segnalava in nessun modo una nuova uscita.
La card fissata della WebTV mostrava da mesi la stessa insegna, con la
pillola verde "Nuova sezione" che a forza di restare li' non segnalava piu'
niente. Chi arrivava sulla home non sapeva che era uscito un TG nuovo.

Questo script trasforma quella card da insegna a VETRINA: miniatura vera
dell'ultima uscita, titolo, data, e una pillola che dice cosa e' e quando.
Alla pubblicazione successiva si cambia una riga di novita.json e si rilancia:
la card si aggiorna da sola e quella vecchia sparisce, senza che nessuno
debba ricordarsi di spegnere niente.

DUE COSE DA SAPERE PRIMA DI TOCCARLO
------------------------------------
1) La card e' FISSATA (data-pa-pin="1"): `ruota_home.py` non la sposta e non
   la conta nel limite delle 6 pubblicazioni in home. Se si toglie quel
   attributo, la card comincia a scorrere verso l'archivio. Non toglierlo.

2) Per trovare dove finisce la card NON si contano i tag di chiusura: dentro
   ci sono <div> annidati e si taglia nel punto sbagliato. E' la stessa
   trappola gia' pagata scrivendo `allinea_barra_strumento.py` (manuale del
   sito §9). Qui si scandisce bilanciando l'annidamento di <a>.

⚠️ Il link punta a webtv.html e NON direttamente a YouTube: sulla pagina della
WebTV c'e' la nota obbligatoria sulla voce sintetica (art. 50 AI Act). Mandare
la gente dritta al video la salterebbe.
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__)) + '/../'
IDX  = BASE + 'index.html'
DATA = BASE + 'novita.json'

MESI = ('gennaio febbraio marzo aprile maggio giugno luglio agosto '
        'settembre ottobre novembre dicembre').split()

# tipo -> (emoji, colore della pillola)
STILE = {
    'TG':      ('\U0001F4FA', '#c0392b'),   # televisore, rosso — si stacca dall'arancio di APE
    'VIDEO':   ('\U0001F3AC', '#c0392b'),
    'NOTIZIA': ('\U0001F4F0', '#1a8f3c'),
}

ANCORA = '<a href="webtv.html" data-pa-section="homepage-card"'


def data_italiana(iso):
    a, m, g = iso.split('-')
    return f'{int(g)} {MESI[int(m) - 1]} {a}'


def fine_ancora(t, i):
    """Indice subito dopo la </a> che chiude l'ancora aperta in i.

    Bilancia l'annidamento invece di cercare la prima chiusura: dentro la
    card ci sono altri tag e la prima </a> incontrata non e' la sua.
    """
    prof, j = 0, i
    while j < len(t):
        m = re.compile(r'</?a\b').search(t, j)
        if not m:
            raise SystemExit('STOP: card senza chiusura </a>')
        if t[m.start():m.start() + 2] == '</':
            prof -= 1
            if prof == 0:
                return t.index('>', m.end()) + 1
        else:
            prof += 1
        j = m.end()
    raise SystemExit('STOP: card senza chiusura </a>')


def card_html(n):
    emoji, colore = STILE.get(n['tipo'].upper(), STILE['NOTIZIA'])
    if n.get('youtube_id'):
        src = f'https://img.youtube.com/vi/{n["youtube_id"]}/hqdefault.jpg'
        img_style = ('width:190px;min-height:180px;object-fit:cover;'
                     'background:#000;flex-shrink:0;display:block')
    elif n.get('immagine'):
        src = n['immagine']
        img_style = ('width:190px;min-height:180px;object-fit:cover;'
                     'flex-shrink:0;display:block')
    else:
        raise SystemExit('STOP: novita.json senza youtube_id ne immagine')

    return (
        f'{ANCORA} data-pa-pin="1" style="display:flex;align-items:stretch;'
        'border-radius:16px;overflow:hidden;background:rgba(255,255,255,.12);'
        'border:4px solid #e8900a;text-decoration:none;margin-bottom:14px;'
        'min-height:180px">'
        # ⚠️ NIENTE loading="lazy" qui: la card sta in cima alla home, e'
        # l'immagine piu' importante della pagina e va chiesta subito. Col lazy
        # (provato il 28/07/2026) il browser non faceva partire la richiesta
        # nemmeno con la card dentro lo schermo: miniatura vuota.
        f'<img src="{src}" alt="{n["titolo"]} — {data_italiana(n["data"])}" '
        f'fetchpriority="high" decoding="async" style="{img_style}" '
        'width="480" height="360">'
        '<div style="padding:16px 18px;display:flex;flex-direction:column;'
        'justify-content:space-between">'
        '<div>'
        f'<span style="display:inline-block;background:{colore};color:#fff;'
        'font-size:0.69em;font-weight:900;letter-spacing:1px;'
        'text-transform:uppercase;padding:3px 10px;border-radius:50px;'
        f'margin-bottom:6px">{emoji} {n["etichetta"]} &middot; '
        f'{data_italiana(n["data"])}</span><br>'
        '<span style="font-family:montserrat,sans-serif;font-size:.72em;'
        'font-weight:700;color:#ffd580;letter-spacing:1px;'
        f'text-transform:uppercase">{n["occhiello"]}</span>'
        '<h2 style="font-family:montserrat,sans-serif;font-size:1em;'
        'font-weight:700;color:#fff;margin:6px 0 8px;line-height:1.35">'
        f'{n["titolo"]}</h2>'
        '<p style="font-family:merriweather,serif;font-size:.82em;'
        'color:rgba(255,255,255,.82);line-height:1.55;margin:0">'
        f'{n["testo"]}</p></div>'
        '<span style="font-family:montserrat,sans-serif;font-size:.75em;'
        'color:#ffd580;font-weight:700;margin-top:10px">'
        '&#x1F4FA; GUARDA ORA</span></div></a>'
    )


def main():
    applica = '--applica' in sys.argv
    n = json.load(open(DATA, encoding='utf-8'))['ultima']
    for campo in ('tipo', 'etichetta', 'titolo', 'data', 'link', 'occhiello', 'testo'):
        if not n.get(campo):
            raise SystemExit(f'STOP: novita.json, campo "{campo}" vuoto')

    t = open(IDX, encoding='utf-8').read()
    if t.count(ANCORA) != 1:
        raise SystemExit(f'STOP: card WebTV trovata {t.count(ANCORA)} volte in '
                         'index.html (attesa 1). Non tocco niente.')

    i = t.index(ANCORA)
    j = fine_ancora(t, i)
    nuova = card_html(n)

    print(f'  tipo      {n["tipo"]}')
    print(f'  etichetta {n["etichetta"]} · {data_italiana(n["data"])}')
    print(f'  titolo    {n["titolo"]}')
    print(f'  link      {n["link"]}')
    print(f'  card      {j - i} caratteri -> {len(nuova)}')

    if not applica:
        print('\n(anteprima: rilanciare con --applica per scrivere)')
        return

    open(IDX, 'w', encoding='utf-8').write(t[:i] + nuova + t[j:])
    print(f'\nOK card aggiornata in {IDX}')
    print('Ora rilancia anche:  python3 aggiorna_ticker.py')


if __name__ == '__main__':
    main()
