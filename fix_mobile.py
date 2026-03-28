file = 'index.html'

with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

errors = []

# 1. Hero principale (riga 224) — griglia 2 colonne hero
old1 = '<div style="max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start;">'
new1 = '<div class="mob-1col" style="max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start;">'
if old1 in content:
    content = content.replace(old1, new1, 1)
    print('OK 1: hero principale')
else:
    errors.append('ERRORE 1: hero principale non trovato')

# 2. Due card nell'hero (riga 282)
old2 = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start;">'
new2 = '<div class="mob-1col" style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start;">'
if old2 in content:
    content = content.replace(old2, new2, 1)
    print('OK 2: due card hero')
else:
    errors.append('ERRORE 2: due card hero non trovate')

# 3. Box Perché PA 3 colonne (riga 323)
old3 = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-bottom:52px;">'
new3 = '<div class="mob-1col" style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-bottom:52px;">'
if old3 in content:
    content = content.replace(old3, new3, 1)
    print('OK 3: box perché PA')
else:
    errors.append('ERRORE 3: box perché PA non trovato')

# 4. Schede rappresentanti Napoli 3 colonne (riga 367)
old4 = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">'
new4 = '<div class="mob-1col" style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">'
if old4 in content:
    content = content.replace(old4, new4, 1)
    print('OK 4: schede Napoli')
else:
    errors.append('ERRORE 4: schede Napoli non trovate')

# 5. Sezione Napoli hero (riga 410)
old5 = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start;">'
new5 = '<div class="mob-1col" style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start;">'
if old5 in content:
    content = content.replace(old5, new5, 1)
    print('OK 5: sezione Napoli')
else:
    errors.append('ERRORE 5: sezione Napoli non trovata')

# 6. Sezione Chi siamo inline (riga 436)
old6 = '<div style="max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start;">'
new6 = '<div class="mob-1col" style="max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start;">'
if old6 in content:
    content = content.replace(old6, new6, 1)
    print('OK 6: sezione chi siamo')
else:
    errors.append('ERRORE 6: sezione chi siamo non trovata')

# 7. Testimonianza box flex (sezione perché PA)
old7 = '<div style="background:linear-gradient(120deg,#8a4e00 0%,#e8900a 100%);border-radius:16px;padding:36px 40px;display:flex;align-items:center;gap:32px;flex-wrap:wrap;">'
new7 = '<div class="mob-flex-col" style="background:linear-gradient(120deg,#8a4e00 0%,#e8900a 100%);border-radius:16px;padding:36px 40px;display:flex;align-items:center;gap:32px;flex-wrap:wrap;">'
if old7 in content:
    content = content.replace(old7, new7, 1)
    print('OK 7: testimonianza')
else:
    errors.append('ERRORE 7: testimonianza non trovata')

# 8. Aggiungo il CSS mobile nel blocco @media esistente
old_media = '  .hero-content{padding:60px 24px;}\n}'
new_media = '''  .hero-content{padding:60px 24px;}

  /* === RESPONSIVE MOBILE === */
  .mob-1col{grid-template-columns:1fr !important;gap:20px !important;}
  .mob-flex-col{flex-direction:column !important;padding:24px 20px !important;gap:16px !important;}

  /* Hero section padding */
  section[style*="padding:64px 48px"]{padding:36px 16px !important;}

  /* Sezione Perché PA padding */
  #perche-pa{padding:40px 16px !important;}

  /* Topbar su mobile */
  .topbar{flex-wrap:wrap;padding:6px 16px;gap:4px;}
  .topbar > div{flex-wrap:wrap;gap:2px;}
}'''

if old_media in content:
    content = content.replace(old_media, new_media)
    print('OK 8: CSS mobile aggiunto')
else:
    errors.append('ERRORE 8: blocco @media non trovato')

if errors:
    for e in errors:
        print(e)
else:
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
    print('FATTO — file salvato')
