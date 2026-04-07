#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Script: crea_congresso_bp.py
# Crea spanu-congresso-bp.html + card hero in index.html + sitemap + llms.txt
# Seguire il manuale v13 — path assoluti, json.dumps per FAQPage

import json, re, os
from PIL import Image

base = '/Users/osxssd/Desktop/partecipazioneattiva/'

# ---------------------------------------------------------------------------
# 0. CONVERTI congresso-nazionale-2026.jpg → images/congresso-bp-2026.webp
# ---------------------------------------------------------------------------
jpg_src = base + 'congresso-nazionale-2026.jpg'
webp_dst = base + 'images/congresso-bp-2026.webp'

if os.path.exists(jpg_src):
    img = Image.open(jpg_src)
    img.save(webp_dst, 'WEBP', quality=82)
    w, h = img.size
    print(f'0. Immagine convertita: {w}x{h}px → images/congresso-bp-2026.webp')
else:
    # Se già convertita o non presente, usa dimensioni di fallback
    w, h = 800, 600
    print('0. congresso-nazionale-2026.jpg non trovato — uso dimensioni 800x600 (aggiorna manualmente)')

# ---------------------------------------------------------------------------
# 1. CREA spanu-congresso-bp.html
# ---------------------------------------------------------------------------

faq_data = [
    {
        "@type": "Question",
        "name": "Quando si tiene il Congresso Nazionale di Base Popolare?",
        "acceptedAnswer": {
            "@type": "Answer",
            "text": "Il Congresso Nazionale di Base Popolare si terrà sabato 11 aprile 2026 a partire dalle ore 09:00 presso la Sala Umberto, Via della Mercede 50, Roma."
        }
    },
    {
        "@type": "Question",
        "name": "Chi rappresenta Partecipazione Attiva al Congresso di Base Popolare?",
        "acceptedAnswer": {
            "@type": "Answer",
            "text": "Luigi Spanu, Portavoce di Partecipazione Attiva, porterà l'intervento del movimento al Congresso Nazionale di Base Popolare dell'11 aprile 2026."
        }
    },
    {
        "@type": "Question",
        "name": "Perché Partecipazione Attiva partecipa al Congresso di Base Popolare?",
        "acceptedAnswer": {
            "@type": "Answer",
            "text": "Partecipazione Attiva condivide con Base Popolare i valori del riformismo popolare, la visione europea e l'impegno per una politica al servizio dei cittadini. La partecipazione al Congresso Nazionale è un'occasione di confronto e dialogo con le forze politiche che credono in una democrazia reale e partecipata."
        }
    }
]

schema = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "NewsArticle",
            "headline": "Spanu al Congresso Nazionale di Base Popolare — 11 aprile",
            "description": "Luigi Spanu porta la voce di Partecipazione Attiva al Congresso Nazionale di Base Popolare, sabato 11 aprile 2026 a Roma.",
            "image": "https://partecipazioneattiva.github.io/images/congresso-bp-2026.webp",
            "datePublished": "2026-04-07",
            "dateModified": "2026-04-07",
            "author": {
                "@type": "Person",
                "name": "Luigi Spanu",
                "jobTitle": "Portavoce di Partecipazione Attiva",
                "image": "https://partecipazioneattiva.github.io/images/organigramma/luigi-spanu.webp",
                "url": "https://partecipazioneattiva.github.io/organigramma.html"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Partecipazione Attiva",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://partecipazioneattiva.github.io/LOGO-PA.webp"
                }
            },
            "mainEntityOfPage": "https://partecipazioneattiva.github.io/spanu-congresso-bp.html"
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://partecipazioneattiva.github.io/"},
                {"@type": "ListItem", "position": 2, "name": "Battaglie", "item": "https://partecipazioneattiva.github.io/battaglie.html"},
                {"@type": "ListItem", "position": 3, "name": "Spanu al Congresso Base Popolare", "item": "https://partecipazioneattiva.github.io/spanu-congresso-bp.html"}
            ]
        },
        {
            "@type": "FAQPage",
            "mainEntity": faq_data
        }
    ]
}

schema_json = json.dumps(schema, ensure_ascii=False, indent=2)

html = f'''<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Spanu al Congresso Base Popolare — 11 aprile 2026</title>
  <meta name="description" content="Luigi Spanu porta la voce di Partecipazione Attiva al Congresso Nazionale di Base Popolare, sabato 11 aprile 2026, Sala Umberto Roma.">
  <link rel="canonical" href="https://partecipazioneattiva.github.io/spanu-congresso-bp.html">
  <link rel="alternate" hreflang="it" href="https://partecipazioneattiva.github.io/spanu-congresso-bp.html">

  <!-- OG + Twitter -->
  <meta property="og:title" content="Spanu al Congresso Nazionale di Base Popolare — 11 aprile">
  <meta property="og:description" content="Luigi Spanu porta la voce di Partecipazione Attiva al Congresso Nazionale di Base Popolare, sabato 11 aprile 2026 a Roma.">
  <meta property="og:image" content="https://partecipazioneattiva.github.io/images/congresso-bp-2026.webp">
  <meta property="og:url" content="https://partecipazioneattiva.github.io/spanu-congresso-bp.html">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary_large_image">

  <!-- GA4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-C0VVYWW9EM"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","G-C0VVYWW9EM");</script>

  <!-- Clarity -->
  <script>(function(e,t,n,s,o,i,a){{e[n]=e[n]||function(){{(e[n].q=e[n].q||[]).push(arguments)}},i=t.createElement(s),i.async=1,i.src="https://www.clarity.ms/tag/"+o,a=t.getElementsByTagName(s)[0],a.parentNode.insertBefore(i,a)}})(window,document,"clarity","script","w3i2jjth4h")</script>

  <!-- Schema.org -->
  <script type="application/ld+json">
{schema_json}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
  <link rel="icon" type="image/png" href="images/favicon.png">
  <link rel="manifest" href="manifest.json">

  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:"Inter",sans-serif;background:#f5f0e8;color:#1a1a1a}}
    /* TOPBAR */
    .topbar{{background:#b8860b;color:#fff;font-size:0.78rem;padding:6px 20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px}}
    .topbar a{{color:#fff;text-decoration:none;font-weight:600}}
    /* NAVBAR */
    nav{{background:#fff;box-shadow:0 2px 8px rgba(0,0,0,.08);position:sticky;top:0;z-index:100}}
    .nav-inner{{max-width:1200px;margin:0 auto;padding:0 20px}}
    .nav-row{{display:flex;align-items:center;justify-content:space-between;padding:12px 0 4px}}
    .logo-area{{display:flex;align-items:center;gap:10px;text-decoration:none}}
    .logo-area img{{height:52px;width:auto}}
    .logo-text{{display:flex;flex-direction:column;line-height:1.1}}
    .logo-text strong{{font-size:1.15rem;font-weight:800;color:#b8860b}}
    .logo-text span{{font-size:0.68rem;letter-spacing:.12em;color:#666;text-transform:uppercase}}
    .nav-links{{display:flex;align-items:center;gap:24px;flex-wrap:wrap}}
    .nav-links a{{text-decoration:none;font-size:0.82rem;font-weight:700;color:#333;letter-spacing:.04em;text-transform:uppercase;transition:color .2s}}
    .nav-links a:hover,.nav-links a.active{{color:#b8860b}}
    .nav-links .dot{{color:#b8860b;font-size:1.1rem}}
    .nav-btns{{display:flex;gap:10px}}
    .btn-iscriviti{{background:#b8860b;color:#fff;border:none;padding:9px 18px;border-radius:24px;font-weight:700;font-size:0.82rem;cursor:pointer;text-decoration:none;transition:background .2s}}
    .btn-iscriviti:hover{{background:#9a7009}}
    .btn-sostienici{{background:transparent;color:#b8860b;border:2px solid #b8860b;padding:7px 16px;border-radius:24px;font-weight:700;font-size:0.82rem;cursor:pointer;text-decoration:none;transition:all .2s}}
    .btn-sostienici:hover{{background:#b8860b;color:#fff}}
    .nav-row2{{display:flex;align-items:center;gap:24px;padding:4px 0 10px;flex-wrap:wrap}}
    .nav-row2 a{{text-decoration:none;font-size:0.82rem;font-weight:700;color:#333;letter-spacing:.04em;text-transform:uppercase;transition:color .2s}}
    .nav-row2 a:hover{{color:#b8860b}}
    .nav-row2 .parlero-wrap{{display:flex;flex-direction:column;line-height:1.1}}
    .nav-row2 .parlero-sub{{font-size:0.62rem;color:#999;font-weight:400;letter-spacing:.05em;text-transform:uppercase}}
    /* BURGER */
    .burger{{display:none;flex-direction:column;gap:5px;cursor:pointer;padding:4px;background:none;border:none;aria-label:"Menu"}}
    .burger span{{display:block;width:24px;height:2px;background:#333;transition:.3s}}
    .mobile-menu{{display:none;flex-direction:column;gap:0;background:#fff;border-top:1px solid #eee}}
    .mobile-menu a{{padding:14px 20px;text-decoration:none;font-weight:700;font-size:0.9rem;color:#333;border-bottom:1px solid #f0e8d0;letter-spacing:.04em;text-transform:uppercase}}
    .mobile-menu a:hover{{color:#b8860b;background:#fdf8ee}}
    .mobile-menu.open{{display:flex}}
    /* ARTICLE */
    .article-wrap{{max-width:780px;margin:48px auto;padding:0 20px 60px}}
    .article-meta{{display:flex;align-items:center;gap:10px;margin-bottom:18px;flex-wrap:wrap}}
    .badge-new{{background:#b8860b;color:#fff;font-size:0.72rem;font-weight:700;padding:4px 12px;border-radius:12px;letter-spacing:.06em;text-transform:uppercase}}
    .article-date{{font-size:0.85rem;color:#888}}
    .article-author{{font-size:0.85rem;color:#555;font-weight:600}}
    h1{{font-size:2rem;font-weight:800;color:#1a1a1a;line-height:1.2;margin-bottom:18px}}
    .article-img{{width:100%;height:auto;display:block;border-radius:12px;margin:24px 0;box-shadow:0 4px 18px rgba(0,0,0,.10)}}
    .article-body{{font-size:1.05rem;line-height:1.75;color:#333}}
    .article-body p{{margin-bottom:1.2em}}
    .article-body h2{{font-size:1.3rem;font-weight:700;color:#b8860b;margin:2em 0 0.6em}}
    .article-body ul{{margin:0.8em 0 1.2em 1.4em}}
    .article-body li{{margin-bottom:0.5em}}
    .info-box{{background:#fff8e6;border-left:4px solid #b8860b;border-radius:8px;padding:18px 20px;margin:28px 0;font-size:0.97rem}}
    .info-box strong{{display:block;margin-bottom:6px;color:#b8860b;font-size:1rem}}
    /* LEGGI ANCHE */
    .leggi-anche{{background:#fff;border-radius:12px;padding:24px;margin-top:40px;box-shadow:0 2px 12px rgba(0,0,0,.06)}}
    .leggi-anche h3{{font-size:0.8rem;font-weight:700;color:#b8860b;letter-spacing:.1em;text-transform:uppercase;margin-bottom:14px}}
    .leggi-anche a{{display:block;padding:10px 0;border-bottom:1px solid #f0e8d0;text-decoration:none;color:#333;font-weight:600;font-size:0.95rem;transition:color .2s}}
    .leggi-anche a:last-child{{border-bottom:none}}
    .leggi-anche a:hover{{color:#b8860b}}
    /* FOOTER */
    footer{{background:#1a1a1a;color:#ccc;padding:40px 20px;text-align:center;font-size:0.85rem}}
    footer a{{color:#b8860b;text-decoration:none}}
    /* MODAL */
    .modal-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:999;align-items:center;justify-content:center}}
    .modal-overlay.open{{display:flex}}
    .modal-box{{background:#fff;border-radius:16px;padding:32px;max-width:420px;width:90%;position:relative;box-shadow:0 8px 40px rgba(0,0,0,.15)}}
    .modal-close{{position:absolute;top:12px;right:16px;font-size:1.4rem;cursor:pointer;color:#999;background:none;border:none}}
    .modal-box h3{{font-size:1.2rem;font-weight:800;margin-bottom:16px;color:#1a1a1a}}
    .modal-box p{{font-size:0.92rem;color:#444;margin-bottom:10px;line-height:1.5}}
    .iban-box{{background:#f5f0e8;border-radius:8px;padding:12px 16px;font-family:monospace;font-size:0.95rem;color:#b8860b;font-weight:700;letter-spacing:.05em;margin:10px 0}}
    /* RESPONSIVE */
    @media(max-width:768px){{
      .nav-links,.nav-row2,.nav-btns{{display:none}}
      .burger{{display:flex}}
      h1{{font-size:1.5rem}}
    }}
  </style>
</head>
<body>

<!-- TOPBAR -->
<div class="topbar">
  <span>📣 Movimento Politico dei Cittadini — <a href="index.html">partecipazioneattiva.github.io</a></span>
  <span>✉️ <a href="mailto:partecipazioneattiva21@gmail.com">partecipazioneattiva21@gmail.com</a></span>
</div>

<!-- NAVBAR -->
<nav>
  <div class="nav-inner">
    <div class="nav-row">
      <a href="index.html" class="logo-area">
        <img src="LOGO-PA.webp" alt="Logo Partecipazione Attiva" width="52" height="52">
        <div class="logo-text">
          <strong>Partecipazione Attiva</strong>
          <span>Movimento Politico</span>
        </div>
      </a>
      <div class="nav-links">
        <a href="index.html">HOME</a>
        <span class="dot">•</span>
        <a href="napoli.html">NAPOLI</a>
        <a href="territori.html">TERRITORI</a>
        <a href="battaglie.html">BATTAGLIE</a>
        <a href="chisiamo.html">CHI SIAMO</a>
        <a href="documenti.html">DOCUMENTI</a>
        <a href="organigramma.html">ORGANIGRAMMA</a>
      </div>
      <div class="nav-btns">
        <a href="https://forms.gle/9xFU3E76zMo8m1gT6" target="_blank" rel="noopener" class="btn-iscriviti">Iscriviti — è gratis</a>
        <button class="btn-sostienici" onclick="document.getElementById('modalSostieni').classList.add('open')">Sostienici</button>
      </div>
      <button class="burger" aria-label="Menu" onclick="document.querySelector('.mobile-menu').classList.toggle('open')">
        <span></span><span></span><span></span>
      </button>
    </div>
    <div class="nav-row2">
      <a href="parlero.html" class="parlero-wrap">
        <span>PARLERÒ</span>
        <span class="parlero-sub">Salotto Culturale</span>
      </a>
      <a href="newsfb.html">NEWS FB</a>
      <a href="youtube.html">YOUTUBE</a>
    </div>
  </div>
  <div class="mobile-menu">
    <a href="index.html">HOME</a>
    <a href="napoli.html">NAPOLI</a>
    <a href="territori.html">TERRITORI</a>
    <a href="battaglie.html">BATTAGLIE</a>
    <a href="chisiamo.html">CHI SIAMO</a>
    <a href="documenti.html">DOCUMENTI</a>
    <a href="organigramma.html">ORGANIGRAMMA</a>
    <a href="parlero.html">PARLERÒ — Salotto Culturale</a>
    <a href="newsfb.html">NEWS FB</a>
    <a href="youtube.html">YOUTUBE</a>
    <a href="https://forms.gle/9xFU3E76zMo8m1gT6" target="_blank" rel="noopener">Iscriviti — è gratis</a>
  </div>
</nav>

<!-- MODAL SOSTIENICI -->
<div class="modal-overlay" id="modalSostieni">
  <div class="modal-box">
    <button class="modal-close" onclick="document.getElementById('modalSostieni').classList.remove('open')" aria-label="Chiudi">×</button>
    <h3>💛 Sostieni Partecipazione Attiva</h3>
    <p>Il tuo contributo ci permette di portare avanti le battaglie per i diritti dei cittadini.</p>
    <p><strong>Bonifico bancario:</strong></p>
    <div class="iban-box">IT60 X076 0115 8000 0104 3110 679</div>
    <p>Intestato a: <strong>Partecipazione Attiva APS</strong></p>
    <p style="margin-top:14px"><strong>Oppure con PayPal:</strong></p>
    <p><a href="https://paypal.me/partecipazioneattiva" target="_blank" rel="noopener" style="color:#b8860b;font-weight:700">paypal.me/partecipazioneattiva</a></p>
  </div>
</div>

<!-- ARTICLE -->
<main>
  <article class="article-wrap">

    <div class="article-meta">
      <span class="badge-new">🗓️ EVENTO — 11 APRILE 2026</span>
      <span class="article-date">7 aprile 2026</span>
    </div>

    <p class="article-author">Luigi Spanu — Portavoce di Partecipazione Attiva</p>

    <h1>Spanu al Congresso Nazionale di Base Popolare: Partecipazione Attiva porta la sua voce a Roma</h1>

    <img
      src="images/congresso-bp-2026.webp"
      alt="Manifesto Congresso Nazionale Base Popolare — 11 aprile 2026, Sala Umberto Roma"
      class="article-img"
      width="{w}" height="{h}"
      loading="lazy"
    >

    <div class="article-body">

      <p><strong>Sabato 11 aprile 2026</strong>, Luigi Spanu parteciperà al <strong>Congresso Nazionale di Base Popolare</strong> a Roma, portando l'intervento di <strong>Partecipazione Attiva</strong>. L'appuntamento è fissato alle ore 09:00 presso la <strong>Sala Umberto, Via della Mercede 50</strong>.</p>

      <div class="info-box">
        <strong>📍 Dettagli dell'evento</strong>
        <strong>Quando:</strong> Sabato 11 aprile 2026 — ore 09:00<br>
        <strong>Dove:</strong> Sala Umberto, Via della Mercede 50, Roma<br>
        <strong>Chi:</strong> Luigi Spanu, Portavoce di Partecipazione Attiva
      </div>

      <h2>Un confronto tra forze riformiste</h2>
      <p>Il Congresso Nazionale di Base Popolare rappresenta un'importante occasione di confronto tra le forze politiche che credono in una democrazia autentica, nel riformismo popolare e nel progetto europeo. Partecipazione Attiva ha scelto di essere presente, in linea con la propria vocazione al dialogo e alla costruzione di reti tra movimenti civici e politici che mettono i cittadini al centro.</p>

      <h2>I temi dell'intervento di Spanu</h2>
      <p>L'intervento di Luigi Spanu toccherà i temi fondamentali del programma di Partecipazione Attiva: la riforma del sistema di finanziamento pubblico, la trasparenza nelle istituzioni, e la necessità di dare voce ai cittadini nelle scelte che li riguardano. Un messaggio chiaro: <em>la politica deve tornare a essere uno strumento al servizio delle persone, non dei poteri forti.</em></p>

      <h2>Base Popolare e il PPE</h2>
      <p>Base Popolare è il partito italiano aderente al <strong>Partito Popolare Europeo (PPE)</strong>, la principale famiglia politica del centro europeo. Il Congresso Nazionale è il momento in cui il partito definisce le sue linee programmatiche e rinnova la sua classe dirigente. La presenza di Partecipazione Attiva testimonia la volontà di costruire ponti tra sensibilità politiche diverse, unite dai valori della partecipazione democratica.</p>

    </div>

    <!-- LEGGI ANCHE -->
    <div class="leggi-anche">
      <h3>Leggi anche</h3>
      <a href="spanu-sire.html">SIRE: finanziare le emergenze senza debito — 9 aprile alla Camera</a>
      <a href="stabilicum.html">Stabilicum: il progetto di legge che cambia tutto</a>
      <a href="spanu-stabilicum.html">Luigi Spanu e l'iter parlamentare dello Stabilicum</a>
      <a href="battaglie.html">Tutte le battaglie di Partecipazione Attiva</a>
    </div>

  </article>
</main>

<!-- FOOTER -->
<footer>
  <p>© 2026 <strong>Partecipazione Attiva</strong> — Movimento Politico dei Cittadini</p>
  <p style="margin-top:8px">
    <a href="privacy.html">Privacy & Cookie Policy</a> ·
    <a href="https://www.facebook.com/PartecipazioneAttiva21/" target="_blank" rel="noopener">Facebook</a> ·
    <a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener">YouTube</a>
  </p>
</footer>

</body>
</html>
'''

with open(base + 'spanu-congresso-bp.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('1. spanu-congresso-bp.html creato')

# ---------------------------------------------------------------------------
# 2. AGGIUNGI CARD HERO IN index.html — PRIMA di tutte le altre card
# ---------------------------------------------------------------------------
with open(base + 'index.html', 'r', encoding='utf-8') as f:
    content = f.read()

card = '''<a href="spanu-congresso-bp.html" style="display:flex;align-items:stretch;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08);text-decoration:none;color:inherit;transition:box-shadow .2s" onmouseover="this.style.boxShadow='0 6px 24px rgba(0,0,0,.14)'" onmouseout="this.style.boxShadow='0 2px 12px rgba(0,0,0,.08)'">
  <div style="width:220px;min-width:220px;overflow:hidden;flex-shrink:0">
    <img src="images/organigramma/luigi-spanu.webp" alt="Luigi Spanu al Congresso Base Popolare" style="width:100%;height:100%;object-fit:cover;display:block" loading="lazy">
  </div>
  <div style="padding:22px 24px;display:flex;flex-direction:column;justify-content:center;gap:8px">
    <span style="background:#f5f0e8;color:#b8860b;font-size:0.72rem;font-weight:700;padding:5px 14px;border-radius:12px;letter-spacing:.06em;text-transform:uppercase;width:fit-content">🆕 NUOVO — 7 APRILE 2026</span>
    <p style="font-size:0.85rem;color:#888;margin:0">Luigi Spanu — Portavoce PA</p>
    <p style="font-size:1.05rem;font-weight:700;color:#1a1a1a;margin:0;line-height:1.3">Spanu al Congresso Nazionale di Base Popolare — 11 aprile a Roma</p>
    <span style="color:#b8860b;font-weight:700;font-size:0.9rem">Leggi l\'articolo →</span>
  </div>
</a>
'''

# Inserisce la nuova card PRIMA della card SIRE (quella più recente precedente)
target = 'loadHeroNews()</script><a href="spanu-sire.html"'
if target in content:
    content = content.replace(target, 'loadHeroNews()</script>' + card + '<a href="spanu-sire.html"')
    print('2. Card hero inserita prima di spanu-sire')
else:
    # Fallback: cerca il primo <a href nell'area hero dopo loadHeroNews
    target2 = 'loadHeroNews()</script>'
    if target2 in content:
        content = content.replace(target2, target2 + card, 1)
        print('2. Card hero inserita (fallback dopo loadHeroNews)')
    else:
        print('2. ⚠️  ATTENZIONE: target non trovato — card NON inserita. Verifica manualmente index.html')

with open(base + 'index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# ---------------------------------------------------------------------------
# 3. AGGIORNA sitemap.xml
# ---------------------------------------------------------------------------
with open(base + 'sitemap.xml', 'r', encoding='utf-8') as f:
    sm = f.read()

new_url = '''  <url>
    <loc>https://partecipazioneattiva.github.io/spanu-congresso-bp.html</loc>
    <lastmod>2026-04-07</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>'''

if 'spanu-congresso-bp.html' not in sm:
    sm = sm.replace('</urlset>', new_url + '\n</urlset>')
    with open(base + 'sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sm)
    print('3. Sitemap aggiornata')
else:
    print('3. URL già in sitemap — nessuna modifica')

# ---------------------------------------------------------------------------
# 4. AGGIORNA llms.txt
# ---------------------------------------------------------------------------
llms_path = base + 'llms.txt'
if os.path.exists(llms_path):
    with open(llms_path, 'r', encoding='utf-8') as f:
        llms = f.read()
    entry = '- Spanu al Congresso Nazionale di Base Popolare (11 aprile 2026): https://partecipazioneattiva.github.io/spanu-congresso-bp.html'
    if 'spanu-congresso-bp' not in llms:
        # Aggiunge dopo la prima riga della sezione articoli
        llms = llms.replace('- SIRE:', entry + '\n- SIRE:', 1)
        with open(llms_path, 'w', encoding='utf-8') as f:
            f.write(llms)
        print('4. llms.txt aggiornato')
    else:
        print('4. Voce già in llms.txt')
else:
    print('4. llms.txt non trovato — skip')

print('\n✅ TUTTO FATTO. Ora esegui lo Step 2:')
print('cd ~/Desktop/partecipazioneattiva && npx pagefind --site . --output-path pagefind && python3 indexnow.py && git add . && git commit -m "nuovo articolo: Spanu al Congresso Nazionale Base Popolare 11 aprile 2026" && git push')
