import os

# ============================================================
# STEP 1: Favicon in tutte le pagine
# ============================================================
pagine = ['index.html', 'napoli.html', 'parlero.html', 'territori.html',
          'organigramma.html', 'battaglie.html', 'privacy.html']

favicon_tag = '<link rel="icon" type="image/webp" href="LOGO-PA.webp">\n<link rel="apple-touch-icon" href="LOGO-PA.webp">\n'

ok_favicon = 0
for filename in pagine:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'rel="icon"' in content:
        print(f'SKIP favicon: {filename} (già presente)')
        continue
    content = content.replace('<link rel="preconnect"', favicon_tag + '<link rel="preconnect"', 1)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    ok_favicon += 1
    print(f'OK favicon: {filename}')

print(f'Favicon: {ok_favicon} pagine aggiornate')

# ============================================================
# STEP 2: Pagina 404 personalizzata
# ============================================================
page_404 = '''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pagina non trovata — Partecipazione Attiva</title>
<link rel="icon" type="image/webp" href="LOGO-PA.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&family=Merriweather:wght@700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Montserrat',sans-serif;background:linear-gradient(120deg,#8a4e00 0%,#e8900a 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:32px;}
.box{background:#fff;border-radius:24px;padding:52px 40px;max-width:480px;width:100%;box-shadow:0 8px 40px rgba(0,0,0,0.15);}
.logo{height:72px;margin-bottom:24px;}
h1{font-family:'Merriweather',serif;font-size:4em;color:#e8900a;line-height:1;margin-bottom:8px;}
h2{font-size:1.1em;color:#8a4e00;font-weight:700;margin-bottom:16px;}
p{color:#666;font-size:.9em;line-height:1.6;margin-bottom:32px;}
a.btn{display:inline-block;background:#e8900a;color:#fff;padding:13px 32px;border-radius:50px;text-decoration:none;font-weight:700;font-size:.9em;transition:background .2s;}
a.btn:hover{background:#8a4e00;}
</style>
</head>
<body>
<div class="box">
  <img src="LOGO-PA.webp" alt="Logo Partecipazione Attiva" class="logo">
  <h1>404</h1>
  <h2>Pagina non trovata</h2>
  <p>La pagina che stai cercando non esiste o è stata spostata.<br>Torna alla home per continuare a navigare.</p>
  <a href="/" class="btn">← Torna alla Home</a>
</div>
</body>
</html>'''

with open('404.html', 'w', encoding='utf-8') as f:
    f.write(page_404)
print('OK: 404.html creata')

# ============================================================
# STEP 3: Animazioni fade-in on scroll in index.html
# ============================================================
fade_css = '''
  /* === FADE-IN ON SCROLL === */
  .fade-in{opacity:0;transform:translateY(24px);transition:opacity .6s ease,transform .6s ease;}
  .fade-in.visible{opacity:1;transform:translateY(0);}
'''

fade_js = '''
<script>
(function(){
  var els = document.querySelectorAll('.fade-in');
  if(!els.length) return;
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){e.target.classList.add('visible');io.unobserve(e.target);}
    });
  },{threshold:0.12});
  els.forEach(function(el){io.observe(el);});
})();
</script>
'''

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Aggiungi CSS fade-in nel blocco @media
if '.fade-in{' not in content:
    content = content.replace('  /* === RESPONSIVE MOBILE === */', fade_css + '\n  /* === RESPONSIVE MOBILE === */', 1)
    print('OK: CSS fade-in aggiunto')
else:
    print('SKIP: CSS fade-in già presente')

# Aggiungi classe fade-in alle sezioni principali
sections = [
    'id="perche-pa"',
    'id="napoli"',
    'id="blog"',
    'id="chisiamo"',
    'id="statuto"',
    'id="iscriviti"',
]
for sec in sections:
    old = f'<section {sec}'
    new = f'<section {sec} class="fade-in"'
    if old in content and f'<section {sec} class=' not in content:
        content = content.replace(old, new, 1)
        print(f'OK: fade-in aggiunto a {sec}')

# Aggiungi JS fade-in prima di </body>
if 'IntersectionObserver' not in content:
    content = content.replace('<!-- MODAL SOSTIENICI -->', fade_js + '\n<!-- MODAL SOSTIENICI -->', 1)
    print('OK: JS fade-in aggiunto')
else:
    print('SKIP: JS fade-in già presente')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n=== TUTTO COMPLETATO ===')
