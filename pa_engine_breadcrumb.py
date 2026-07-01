#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Applica 3 patch a pubblica_articolo.py per aggiungere i BREADCRUMB ai NUOVI articoli:
#  1) schema BreadcrumbList (in <head>, accanto al NewsArticle)
#  2) breadcrumb VISIBILE nell'hero (Home > card_cat > card_title)
#  3) aggiorna il self-check: da 1 a 2 blocchi ld+json attesi
# Ogni patch verifica l'ancora esatta (assert). Idempotente: se gia applicata, avvisa e non tocca.
import sys, shutil, os

BASE = '/Users/osxssd/Desktop/LAVORI/partecipazioneattiva/'
if len(sys.argv) > 1: BASE = sys.argv[1] if sys.argv[1].endswith('/') else sys.argv[1] + '/'
ENG = BASE + 'pubblica_articolo.py'

s = open(ENG, encoding='utf-8').read()

if 'BreadcrumbList' in s:
    print('Engine gia con breadcrumb: nessuna modifica.')
    sys.exit(0)

# backup di sicurezza
shutil.copy(ENG, ENG + '.bak')

# ---- PATCH 1 ----
old1 = ("    html = re.sub(r'<script type=\"application/ld\\+json\">.*?</script>',\n"
        "                  '<script type=\"application/ld+json\">'+json.dumps(schema, ensure_ascii=False)+'</script>',\n"
        "                  html, flags=re.DOTALL, count=1)")
new1 = old1 + (
    "\n    # BreadcrumbList: Home > {card_cat|Battaglie} > {h1}\n"
    "    brc_mid = a.get('card_cat') or 'Battaglie'\n"
    "    breadcrumb = {\"@context\":\"https://schema.org\",\"@type\":\"BreadcrumbList\",\"itemListElement\":[\n"
    "        {\"@type\":\"ListItem\",\"position\":1,\"name\":\"Home\",\"item\":U},\n"
    "        {\"@type\":\"ListItem\",\"position\":2,\"name\":brc_mid,\"item\":U+\"battaglie.html\"},\n"
    "        {\"@type\":\"ListItem\",\"position\":3,\"name\":a['h1'],\"item\":U+a['slug']}]}\n"
    "    html = html.replace('</head>',\n"
    "        '<script type=\"application/ld+json\">'+json.dumps(breadcrumb, ensure_ascii=False)+'</script></head>', 1)")
assert s.count(old1) == 1, 'STOP P1: blocco schema NewsArticle non trovato (engine diverso dal previsto)'
s = s.replace(old1, new1, 1)

# ---- PATCH 2 ----
old2 = ('    hero = (f\'<div class="article-hero">\\n  <div class="categoria">{a["categoria_hero"]}</div>\\n\'')
new2 = ("    brc_mid = a.get('card_cat') or 'Battaglie'\n"
        "    brc_vis = (f'<nav class=\"breadcrumb\" aria-label=\"Percorso\" style=\"max-width:820px;margin:0 auto;padding:14px 24px 0;'\n"
        "               f'font-family:montserrat,sans-serif;font-size:.82em;color:#9c5b00\">'\n"
        "               f'<a href=\"index.html\" style=\"color:#9c5b00;text-decoration:none\">Home</a>'\n"
        "               f' <span aria-hidden=\"true\">&rsaquo;</span> '\n"
        "               f'<a href=\"battaglie.html\" style=\"color:#9c5b00;text-decoration:none\">{brc_mid}</a>'\n"
        "               f' <span aria-hidden=\"true\">&rsaquo;</span> '\n"
        "               f'<span style=\"color:#8a4e00\">{a[\"card_title\"]}</span></nav>')\n"
        "    hero = (brc_vis + f'<div class=\"article-hero\">\\n  <div class=\"categoria\">{a[\"categoria_hero\"]}</div>\\n'")
assert s.count(old2) == 1, 'STOP P2: riga hero non trovata (engine diverso dal previsto)'
s = s.replace(old2, new2, 1)

# ---- PATCH 3 ----
old3 = "    if h.count('<script type=\"application/ld+json\">') != 1: errs.append('schema non singolo')"
new3 = "    if h.count('<script type=\"application/ld+json\">') != 2: errs.append('schema: attesi 2 blocchi (NewsArticle + BreadcrumbList)')"
assert s.count(old3) == 1, 'STOP P3: self-check schema non trovato (engine diverso dal previsto)'
s = s.replace(old3, new3, 1)

# validazione sintattica prima di scrivere
import ast
ast.parse(s)
open(ENG, 'w', encoding='utf-8').write(s)
print('OK: 3 patch applicate a pubblica_articolo.py')
print('  1) schema BreadcrumbList in <head>')
print('  2) breadcrumb visibile nell hero (Home > card_cat > card_title)')
print('  3) self-check aggiornato a 2 blocchi schema')
print('Backup salvato in pubblica_articolo.py.bak')
