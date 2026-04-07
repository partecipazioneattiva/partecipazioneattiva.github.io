#!/usr/bin/env python3
# =============================================================
# SCRIPT: pubblica articolo Congresso Base Popolare 11/04/2026
# Esegui con:
#   python3 /tmp/pubblica_congresso_bp.py && rm /tmp/pubblica_congresso_bp.py
# =============================================================

import os, shutil, json
from pathlib import Path

base = Path('/Users/osxssd/Desktop/partecipazioneattiva/')

# ─────────────────────────────────────────────────────────────
# 1. COPIA L'IMMAGINE DEL MANIFESTO
#    Converte il JPG scaricato nella cartella images/ come webp
#    (usa Pillow che è già installato)
# ─────────────────────────────────────────────────────────────
# ISTRUZIONE: prima di eseguire questo script, metti il file
#   congresso-nazionale-2026.jpg  nella cartella del progetto
#   (~/Desktop/partecipazioneattiva/) oppure aggiorna il path
#   qui sotto con il percorso reale del file scaricato.

jpg_src = base / 'congresso-nazionale-2026.jpg'
webp_dst = base / 'images' / 'congresso-base-popolare-2026.webp'

if jpg_src.exists():
    from PIL import Image
    img = Image.open(jpg_src)
    img.save(webp_dst, 'WEBP', quality=82)
    w, h = img.size
    print(f'1. Manifesto convertito in WebP ({w}x{h}px) → images/congresso-base-popolare-2026.webp')
else:
    print(f'⚠️  File {jpg_src} non trovato — metti il JPG del manifesto nella root del progetto e riesegui.')
    print('   (oppure aggiorna jpg_src in questo script con il path corretto)')

# ─────────────────────────────────────────────────────────────
# 2. CREA IL FILE HTML DELL'ARTICOLO
# ─────────────────────────────────────────────────────────────
html_content = open('/tmp/spanu-congresso-base-popolare.html').read() \
    if Path('/tmp/spanu-congresso-base-popolare.html').exists() \
    else None

# Se il file HTML è già presente nella root del progetto, salta
# Altrimenti lo creiamo qui inline (vedi sotto)
# In questo script assumiamo che tu abbia già copiato manualmente
# spanu-congresso-base-popolare.html nella root del progetto
# OPPURE che tu voglia usare il contenuto prodotto da Claude.

html_dst = base / 'spanu-congresso-base-popolare.html'
if not html_dst.exists():
    print('⚠️  Copia prima spanu-congresso-base-popolare.html nella root del progetto.')
    print('   Puoi scaricarlo dall\'output di Claude e copiarlo con:')
    print('   cp ~/Downloads/spanu-congresso-base-popolare.html ~/Desktop/partecipazioneattiva/')
else:
    print('2. File HTML già presente ✅')

# ─────────────────────────────────────────────────────────────
# 3. AGGIUNGI CARD NELL'HERO DI INDEX.HTML
#    La nuova card va PRIMA di tutte le altre (regola #11)
# ─────────────────────────────────────────────────────────────
index_path = base / 'index.html'
with open(index_path, 'r', encoding='utf-8') as f:
    idx = f.read()

NEW_CARD = '''<a href="spanu-congresso-base-popolare.html" style="display:block;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);text-decoration:none;color:inherit;transition:transform .2s" onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='none'">
  <img src="images/congresso-base-popolare-2026.webp" alt="Congresso Nazionale Base Popolare 2026" width="480" height="720" loading="lazy" style="width:100%;height:200px;object-fit:cover;object-position:top;display:block">
  <div style="padding:16px 18px">
    <span style="font-family:Montserrat,sans-serif;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#e8b84b">Evento · 11 Aprile 2026</span>
    <h3 style="font-family:Montserrat,sans-serif;font-size:0.95rem;font-weight:700;color:#1a3a5c;margin:6px 0 8px;line-height:1.3">Spanu al Congresso Nazionale di Base Popolare</h3>
    <p style="font-family:Montserrat,sans-serif;font-size:0.78rem;color:#5c5c5c;line-height:1.5;margin:0">Il Portavoce di Partecipazione Attiva a Roma: regole scritte, battaglie concrete, costruire dal basso.</p>
  </div>
</a>
'''

TARGET = 'loadHeroNews()</script>'
if TARGET in idx and 'spanu-congresso-base-popolare' not in idx:
    idx = idx.replace(TARGET, TARGET + NEW_CARD, 1)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(idx)
    print('3. Card hero aggiunta in index.html ✅')
elif 'spanu-congresso-base-popolare' in idx:
    print('3. Card già presente in index.html — nessuna modifica ✅')
else:
    print('⚠️  Target loadHeroNews() non trovato in index.html — aggiungi la card manualmente.')

# ─────────────────────────────────────────────────────────────
# 4. AGGIORNA SITEMAP.XML
# ─────────────────────────────────────────────────────────────
sitemap_path = base / 'sitemap.xml'
with open(sitemap_path, 'r', encoding='utf-8') as f:
    sm = f.read()

NEW_URL = '''  <url>
    <loc>https://partecipazioneattiva.github.io/spanu-congresso-base-popolare.html</loc>
    <lastmod>2026-04-11</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>'''

if 'spanu-congresso-base-popolare' not in sm:
    sm = sm.replace('</urlset>', NEW_URL + '\n</urlset>')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(sm)
    print('4. Sitemap aggiornata ✅')
else:
    print('4. URL già presente in sitemap — nessuna modifica ✅')

# ─────────────────────────────────────────────────────────────
# 5. AGGIORNA llms.txt
# ─────────────────────────────────────────────────────────────
llms_path = base / 'llms.txt'
if llms_path.exists():
    with open(llms_path, 'r', encoding='utf-8') as f:
        llms = f.read()
    NEW_LLM = '- Spanu al Congresso Nazionale di Base Popolare (11 apr 2026): https://partecipazioneattiva.github.io/spanu-congresso-base-popolare.html'
    if 'spanu-congresso-base-popolare' not in llms:
        # Inserisce dopo la prima voce di Spanu già presente
        llms = llms.replace(
            '- Luigi Spanu',
            NEW_LLM + '\n- Luigi Spanu',
            1
        )
        with open(llms_path, 'w', encoding='utf-8') as f:
            f.write(llms)
        print('5. llms.txt aggiornato ✅')
    else:
        print('5. llms.txt già aggiornato ✅')
else:
    print('5. llms.txt non trovato — aggiorna manualmente')

print('\n✅ Script completato. Ora esegui:')
print('cd ~/Desktop/partecipazioneattiva && npx pagefind --site . --output-path pagefind && python3 indexnow.py && git add . && git commit -m "nuovo articolo: Spanu al Congresso Nazionale Base Popolare 11 aprile 2026" && git push')
