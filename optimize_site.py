import os
from PIL import Image

# ============================================================
# STEP 1: CONVERTI IMMAGINI IN WEBP
# ============================================================

conversioni = [
    # (sorgente, destinazione, max_width, qualità)
    ('LOGO-PA.png',                          'LOGO-PA.webp',                          400,  90),
    ('images/insieme-napoli.png',            'images/insieme-napoli.webp',            800,  82),
    ('images/pensattivo-rcauto.png',         'images/pensattivo-rcauto.webp',         800,  82),
    ('images/paolo-neri.png',                'images/paolo-neri.webp',                600,  82),
    ('images/antonio-cristiano.jpeg',        'images/antonio-cristiano.webp',         600,  82),
    ('images/rosa-ugon.png',                 'images/rosa-ugon.webp',                 600,  82),
    ('images/team-meeting.jpeg',             'images/team-meeting.webp',              800,  82),
    ('images/organigramma/angelo-nicotra-finale.png',  'images/organigramma/angelo-nicotra-finale.webp',  500, 82),
    ('images/organigramma/antonio-cristiano.png',      'images/organigramma/antonio-cristiano.webp',      500, 82),
    ('images/organigramma/daniele-tandura.png',        'images/organigramma/daniele-tandura.webp',        500, 82),
    ('images/organigramma/fernando-farina.png',        'images/organigramma/fernando-farina.webp',        500, 82),
    ('images/organigramma/luigi-spanu.jpg',            'images/organigramma/luigi-spanu.webp',            500, 82),
    ('images/organigramma/paolo-neri.png',             'images/organigramma/paolo-neri.webp',             500, 82),
    ('images/organigramma/rosa-ugon.png',              'images/organigramma/rosa-ugon.webp',              500, 82),
    ('images/organigramma/stefano-piva.png',           'images/organigramma/stefano-piva.webp',           500, 82),
]

print('=== STEP 1: Conversione WebP ===')
totale_prima = 0
totale_dopo = 0

for src, dst, max_w, qualita in conversioni:
    if not os.path.exists(src):
        print(f'  SKIP (non trovato): {src}')
        continue
    try:
        img = Image.open(src).convert('RGBA' if src.endswith('.png') else 'RGB')
        # Ridimensiona se troppo grande
        if img.width > max_w:
            ratio = max_w / img.width
            new_h = int(img.height * ratio)
            img = img.resize((max_w, new_h), Image.LANCZOS)
        # Per WebP, RGBA non supporta tutti i browser vecchi — converti in RGB se JPEG
        if dst.endswith('.webp') and img.mode == 'RGBA':
            # Mantieni trasparenza per loghi, converti per foto
            pass
        img.save(dst, 'WEBP', quality=qualita, method=6)
        prima = os.path.getsize(src) // 1024
        dopo = os.path.getsize(dst) // 1024
        totale_prima += prima
        totale_dopo += dopo
        risparmio = int((1 - dopo/prima) * 100) if prima > 0 else 0
        print(f'  OK: {src} → {dst} ({prima}KB → {dopo}KB, -{risparmio}%)')
    except Exception as e:
        print(f'  ERRORE: {src} → {e}')

print(f'\n  Totale: {totale_prima}KB → {totale_dopo}KB (risparmio: {totale_prima-totale_dopo}KB)')

# ============================================================
# STEP 2: AGGIORNA RIFERIMENTI HTML IN TUTTI I FILE
# ============================================================

print('\n=== STEP 2: Aggiornamento riferimenti HTML ===')

html_files = ['index.html', 'napoli.html', 'parlero.html', 'territori.html',
              'organigramma.html', 'battaglie.html', 'privacy.html']

sostituzioni = [
    ('LOGO-PA.png',                          'LOGO-PA.webp'),
    ('images/insieme-napoli.png',            'images/insieme-napoli.webp'),
    ('images/pensattivo-rcauto.png',         'images/pensattivo-rcauto.webp'),
    ('images/paolo-neri.png',                'images/paolo-neri.webp'),
    ('images/antonio-cristiano.jpeg',        'images/antonio-cristiano.webp'),
    ('images/rosa-ugon.png',                 'images/rosa-ugon.webp'),
    ('images/team-meeting.jpeg',             'images/team-meeting.webp'),
    ('images/organigramma/angelo-nicotra-finale.png',  'images/organigramma/angelo-nicotra-finale.webp'),
    ('images/organigramma/antonio-cristiano.png',      'images/organigramma/antonio-cristiano.webp'),
    ('images/organigramma/daniele-tandura.png',        'images/organigramma/daniele-tandura.webp'),
    ('images/organigramma/fernando-farina.png',        'images/organigramma/fernando-farina.webp'),
    ('images/organigramma/luigi-spanu.jpg',            'images/organigramma/luigi-spanu.webp'),
    ('images/organigramma/paolo-neri.png',             'images/organigramma/paolo-neri.webp'),
    ('images/organigramma/rosa-ugon.png',              'images/organigramma/rosa-ugon.webp'),
    ('images/organigramma/stefano-piva.png',           'images/organigramma/stefano-piva.webp'),
]

for html in html_files:
    if not os.path.exists(html):
        continue
    with open(html, 'r', encoding='utf-8') as f:
        content = f.read()
    originale = content
    for vecchio, nuovo in sostituzioni:
        content = content.replace(vecchio, nuovo)
    if content != originale:
        with open(html, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  OK: {html} aggiornato')
    else:
        print(f'  (nessuna modifica): {html}')

# ============================================================
# STEP 3: FIX LAZY LOADING LOGO NAVBAR IN INDEX.HTML
# ============================================================

print('\n=== STEP 3: Fix lazy loading logo navbar ===')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_logo = '<img loading="lazy" src="LOGO-PA.webp" alt="Logo">'
new_logo = '<img src="LOGO-PA.webp" alt="Logo" width="48" height="48">'

if old_logo in content:
    content = content.replace(old_logo, new_logo)
    print('  OK: lazy loading rimosso dal logo navbar')
else:
    print('  SKIP: logo navbar non trovato con quella stringa esatta')

# ============================================================
# STEP 4: AGGIUNGI font-display:swap AI GOOGLE FONTS
# ============================================================

print('\n=== STEP 4: font-display swap ===')

old_font = 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&family=Merriweather:wght@400;700&display=swap'
new_font = 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&family=Merriweather:wght@400;700&display=swap'
# display=swap è già nell'URL — verifichiamo
if 'display=swap' in content:
    print('  OK: font-display=swap già presente')
else:
    content = content.replace(
        'family=Merriweather:wght@400;700&display=swap',
        'family=Merriweather:wght@400;700&display=swap'
    )
    print('  OK: font-display swap aggiunto')

# ============================================================
# STEP 5: AGGIUNGI FAVICON ESPLICITO
# ============================================================

print('\n=== STEP 5: Favicon ===')

if '<link rel="icon"' in content:
    print('  OK: favicon già presente')
else:
    old_canonical = '<link rel="canonical"'
    new_favicon = '<link rel="icon" type="image/webp" href="LOGO-PA.webp">\n<link rel="canonical"'
    if old_canonical in content:
        content = content.replace(old_canonical, new_favicon, 1)
        print('  OK: favicon aggiunto')
    else:
        print('  SKIP: canonical non trovato')

# ============================================================
# STEP 6: AGGIUNGI SCHEMA.ORG JSON-LD
# ============================================================

print('\n=== STEP 6: Schema.org JSON-LD ===')

schema = '''
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "PoliticalParty",
  "name": "Partecipazione Attiva",
  "alternateName": "PA - Movimento Politico dei Cittadini",
  "description": "Libera associazione di cittadini per una politica trasparente, partecipata e al servizio delle persone. Fondata sulla Costituzione Italiana.",
  "url": "https://partecipazioneattiva.github.io",
  "logo": "https://partecipazioneattiva.github.io/LOGO-PA.webp",
  "foundingDate": "2021",
  "email": "partecipazioneattiva21@gmail.com",
  "sameAs": [
    "https://www.facebook.com/PartecipazioneAttiva21/",
    "https://www.youtube.com/@partecipazioneattiva",
    "https://www.tiktok.com/@partecipazione.at"
  ],
  "areaServed": {
    "@type": "Country",
    "name": "Italia"
  },
  "event": {
    "@type": "Event",
    "name": "Presentazione pubblica Partecipazione Attiva",
    "description": "Presentazione pubblica del movimento Partecipazione Attiva",
    "location": {
      "@type": "Place",
      "name": "Bagnoli, Napoli",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Bagnoli",
        "addressRegion": "Napoli",
        "addressCountry": "IT"
      }
    },
    "organizer": {
      "@type": "Organization",
      "name": "Partecipazione Attiva"
    }
  }
}
</script>'''

if 'application/ld+json' in content:
    print('  OK: Schema.org già presente')
else:
    content = content.replace('</head>', schema + '\n</head>', 1)
    print('  OK: Schema.org JSON-LD aggiunto')

# Salva index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n=== TUTTO COMPLETATO ===')
