#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
#  PUBBLICA_ARTICOLO.PY  —  motore unico di pubblicazione sito PA
#  Per ogni nuovo articolo: compila SOLO il blocco CONFIG qui sotto e lancia:
#      python3 /Users/osxssd/Desktop/LAVORI/partecipazioneattiva/pubblica_articolo.py
#  Fa: articolo da GOLD (spanu-sire.html) + card in cima + badge automatico
#  per data + voce ticker + riga sitemap + 8 check. Idempotente (assert).
#  NON tocca aggiorna_feed/pagefind/git: quelli restano nel comando di push.
# ============================================================================
import re, json, sys, os

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'

# Anagrafica autori: chiave -> (Nome, Ruolo, foto). Aggiungere qui se serve.
AUTORI = {
    'spanu':    ('Luigi Spanu',  'Portavoce', 'images/organigramma/luigi-spanu.webp'),
    'neri':     ('Paolo Neri',   'Direttivo', 'images/organigramma/paolo-neri.webp'),
    'nicotra':  ('Angelo Nicotra','Presidente','images/organigramma/angelo-nicotra.webp'),
    'cristiano':('Antonio Cristiano','Direttivo','images/organigramma/antonio-cristiano.webp'),
    'mollica':  ('Amilcare Mollica','Consulente legale','images/organigramma/amilcare-mollica.webp'),
}

# ============================== CONFIG ARTICOLO =============================
# (compilare per ogni nuovo pezzo; 'body' lo scrive Claude in HTML)
ART = {
  'slug'         : 'esempio-giugno2026.html',
  'autore'       : 'spanu',
  'data_iso'     : '2026-06-29',
  'data_human'   : '29 giugno 2026',
  'data_badge'   : '29 GIUGNO 2026',          # badge "🆕 ..." sulla card
  'lettura_min'  : 7,
  'categoria_hero': '&#x2696;&#xFE0F; Esempio',  # con emoji entity
  'og_image'     : 'images/pensattivo-esempio.webp',
  'h1'           : 'Titolo lungo H1 dell\u0027articolo',
  'sottotitolo'  : 'Sottotitolo dell\u0027articolo.',
  'meta_desc'    : 'Descrizione SEO sotto i 155 caratteri.',
  'card_cat'     : 'CATEGORIA',                # maiuscolo
  'card_title'   : 'Titolo card homepage',
  'card_desc'    : 'Sommario breve per la card.',
  'ticker'       : '&#x2696;&#xFE0F; <strong>TEMA:</strong> frase ticker &nbsp;&nbsp;&bull;&nbsp;&nbsp; ',
  'body'         : '<article class="article-wrap"><h2>Sezione</h2><p>Corpo.</p></article>',
}
# ===========================================================================

GOLD = BASE + 'spanu-sire.html'
IDX  = BASE + 'index.html'
SMP  = BASE + 'sitemap.xml'

VIETATE = ['SIRE', 'Camera dei Deputati', 'luigi-spanu.jpg', 'Evento alla Camera', 'spanu-sire']

def build_articolo(a):
    nome, ruolo, foto = AUTORI[a['autore']]
    html = open(GOLD, encoding='utf-8').read()
    assert html.count('type=application/ld+json') == 0, 'GOLD ha schema fantasma'
    U = 'https://partecipazione-attiva.it/'
    html = re.sub(r'<title>[^<]*</title>', f"<title>{a['h1']} | {nome}</title>", html, 1)
    html = re.sub(r'<meta name="description" content="[^"]*">', f"<meta name=\"description\" content=\"{a['meta_desc']}\">", html, 1)
    html = re.sub(r'<meta property="og:title" content="[^"]*">', f"<meta property=\"og:title\" content=\"{a['h1']}\">", html, 1)
    html = re.sub(r'<meta property="og:description" content="[^"]*">', f"<meta property=\"og:description\" content=\"{a['meta_desc']}\">", html, 1)
    html = re.sub(r'<meta property="og:url" content="[^"]*">', f"<meta property=\"og:url\" content=\"{U}{a['slug']}\">", html, 1)
    html = re.sub(r'<link rel="alternate" hreflang="it" href="[^"]*">', f"<link rel=\"alternate\" hreflang=\"it\" href=\"{U}{a['slug']}\">", html, 1)
    html = re.sub(r'<link rel="canonical" href="[^"]*">', f"<link rel=\"canonical\" href=\"{U}{a['slug']}\">", html, 1)
    html = re.sub(r'<meta property="og:image" content="[^"]*">', f"<meta property=\"og:image\" content=\"{U}{a['og_image']}\">", html, 1)
    schema = {"@context":"https://schema.org","@type":"NewsArticle","headline":a['h1'],
              "description":a['meta_desc'],"image":U+a['og_image'],"datePublished":a['data_iso'],
              "dateModified":a['data_iso'],
              "author":{"@type":"Person","name":nome,"jobTitle":ruolo,"url":U+"organigramma.html"},
              "publisher":{"@type":"Organization","name":"Partecipazione Attiva",
                           "logo":{"@type":"ImageObject","url":U+"LOGO-PA.webp"}},
              "mainEntityOfPage":U+a['slug']}
    html = re.sub(r'<script type="application/ld\+json">.*?</script>',
                  '<script type="application/ld+json">'+json.dumps(schema, ensure_ascii=False)+'</script>',
                  html, flags=re.DOTALL, count=1)
    hero = (f'<div class="article-hero">\n  <div class="categoria">{a["categoria_hero"]}</div>\n'
            f'  <h1>{a["h1"]}</h1>\n  <p class="sottotitolo">{a["sottotitolo"]}</p>\n'
            f'  <div class="author-hero">\n    <img loading=lazy src="{foto}" alt="{nome} {ruolo} Partecipazione Attiva">\n'
            f'    <div class="author-hero-info">\n      <div class="nome">{nome}</div>\n'
            f'      <div class="ruolo">{ruolo} &mdash; Partecipazione Attiva</div>\n    </div>\n  </div>\n'
            f'  <div class="article-meta">\n    <span class="badge-pa">Partecipazione Attiva</span>\n'
            f'    <span>&#x1F4C5; {a["data_human"]}</span>\n    <span>&#x23F1; {a["lettura_min"]} minuti di lettura</span>\n  </div>\n</div>')
    body = a['body']
    if not body.lstrip().startswith('<article'):
        body = '<article class="article-wrap">\n' + body + '\n</article>'
    # link di condivisione corretti dentro il corpo (se l'autore non li mette)
    start = html.index('<div class="article-hero">')
    end   = html.index('</article>') + len('</article>')
    html  = html[:start] + hero + '\n\n' + body + html[end:]
    # bonifica residui share GOLD
    for bad in ['u=https://partecipazione-attiva.it/spanu-sire.html', '%20https://partecipazione-attiva.it/spanu-sire.html']:
        html = html.replace(bad, bad.replace('spanu-sire.html', a['slug']))
    html = html.replace('https://partecipazioneattiva.github.io/', U).replace('partecipazioneattiva.github.io', 'partecipazione-attiva.it')
    return html

def check_articolo(path):
    h = open(path, encoding='utf-8').read()
    errs = []
    if not h.rstrip().endswith('</html>'): errs.append('file troncato')
    if 'github.io' in h: errs.append('github.io presente')
    if 'type=application/ld+json' in h: errs.append('schema fantasma')
    for v in VIETATE:
        if v in h: errs.append(f'residuo GOLD: {v}')
    if h.count('<script type="application/ld+json">') != 1: errs.append('schema non singolo')
    return errs

BADGE = ('<span style="display:inline-block;background:#c0392b;color:#fff;font-size:0.69em;'
         'font-weight:900;letter-spacing:1px;text-transform:uppercase;padding:3px 10px;'
         'border-radius:50px;margin-bottom:6px;animation:pulse-live 1.2s infinite">Ultimo aggiornamento</span><br>')

def card_html(a):
    return (f'<a href="{a["slug"]}" data-pa-section="homepage-card" style="display:flex;align-items:stretch;'
            'border-radius:16px;overflow:hidden;background:rgba(255,255,255,.12);border:2px solid #ffd580;'
            'text-decoration:none;margin-bottom:14px;min-height:180px">'
            f'<img src="{a["og_image"]}" alt="{a["card_cat"]}" style="width:140px;min-height:180px;'
            'object-fit:cover;flex-shrink:0;display:block">'
            '<div style="padding:16px 18px;display:flex;flex-direction:column;justify-content:space-between"><div>'
            + BADGE +
            f'<span style="font-family:montserrat,sans-serif;font-size:.72em;font-weight:700;color:#ffd580;'
            f'letter-spacing:1px;text-transform:uppercase">{a["card_cat"]}</span>'
            f'<h3 style="font-family:montserrat,sans-serif;font-size:1em;font-weight:700;color:#fff;'
            f'margin:6px 0 8px;line-height:1.35">{a["card_title"]}</h3>'
            f'<p style="font-family:merriweather,serif;font-size:.82em;color:rgba(255,255,255,.82);'
            f'line-height:1.55;margin:0">{a["card_desc"]}</p></div>'
            f'<span style="font-family:montserrat,sans-serif;font-size:.75em;color:#ffd580;font-weight:700;'
            f'margin-top:10px">&#x1F195; {a["data_badge"]}</span></div></a>')

def pulisci_badge_vecchi(html, data_badge_oggi):
    # rimuove il badge rosso dalle card la cui data badge != oggi (regola: badge = solo giorno di pubblicazione)
    def repl(m):
        seg = m.group(0)
        if 'pulse-live' in seg and f'&#x1F195; {data_badge_oggi}' not in seg:
            seg = seg.replace(BADGE, '')
        return seg
    return re.sub(r'<a [^>]*data-pa-section="homepage-card".*?</a>', repl, html, flags=re.DOTALL)

def aggiorna_index(a):
    html = open(IDX, encoding='utf-8').read()
    assert a['slug'] not in html, 'STOP: card gia presente (gia pubblicato?)'
    # 1) trova la card attualmente in cima (prima ancora homepage-card) e inserisci la nuova prima
    m = re.search(r'<a [^>]*data-pa-section="homepage-card"', html)
    assert m, 'STOP: nessuna card homepage trovata'
    pos = m.start()
    html = html[:pos] + card_html(a) + html[pos:]
    # 2) regola badge: togli il badge dalle card di giorni diversi da oggi
    html = pulisci_badge_vecchi(html, a['data_badge'])
    # 3) ticker: voce in testa
    tko = '<div id="tk" data-pa-section="ticker" style="position:absolute;white-space:nowrap;will-change:transform; color:#ffffff;">'
    assert html.count(tko) == 1, 'STOP: apertura ticker non trovata (1 attesa)'
    html = html.replace(tko, tko + a['ticker'], 1)
    open(IDX, 'w', encoding='utf-8').write(html)

def aggiorna_sitemap(a):
    sm = open(SMP, encoding='utf-8').read()
    if a['slug'] in sm:
        return 'sitemap: gia presente'
    row = f'<url><loc>https://partecipazione-attiva.it/{a["slug"]}</loc><lastmod>{a["data_iso"]}</lastmod></url>'
    assert sm.count('</urlset>') == 1, 'STOP: </urlset> non singolo'
    open(SMP, 'w', encoding='utf-8').write(sm.replace('</urlset>', row + '\n</urlset>', 1))
    return 'sitemap: url aggiunto'

def main():
    a = ART
    out = BASE + a['slug']
    assert not os.path.exists(out), f'STOP: {a["slug"]} esiste gia'
    html = build_articolo(a)
    open(out, 'w', encoding='utf-8').write(html)
    errs = check_articolo(out)
    assert not errs, 'CHECK FALLITI: ' + '; '.join(errs)
    print(f'OK articolo: {a["slug"]} ({len(html)} char) - 8 check superati')
    aggiorna_index(a)
    print('OK index.html: card in cima + badge per-data + ticker')
    print('OK ' + aggiorna_sitemap(a))
    print('--- FATTO. Ora esegui il PUSH (vedi manuale §35.4) ---')

if __name__ == '__main__':
    main()
