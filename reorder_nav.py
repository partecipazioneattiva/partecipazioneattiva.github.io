with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''  <div class="nav-links">
    <a href="index.html">Home</a><a href="napoli.html" style="color:#e8900a;font-weight:900;">&#9679; Napoli</a><a href="#blog">News FB</a>
    <a href="territori.html">Territori</a><a href="organigramma.html">Organigramma</a><a href="#chisiamo">Chi Siamo</a><a href="parlero.html" style="text-align:center;line-height:1.2;display:inline-flex;flex-direction:column;align-items:center;"><span style="font-weight:900;letter-spacing:.5px;">PARLER&Ograve;</span><span style="font-size:.75em;font-weight:700;color:#8a4e00;text-transform:none;letter-spacing:0;">Salotto Culturale</span></a>
    <a href="#statuto">Documenti</a>
    <a href="battaglie.html">Battaglie</a>
    <a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener noreferrer">YouTube</a>
  </div>'''

new = '''  <div class="nav-links">
    <a href="index.html">Home</a><a href="napoli.html" style="color:#e8900a;font-weight:900;">&#9679; Napoli</a><a href="territori.html">Territori</a><a href="battaglie.html">Battaglie</a><a href="#chisiamo">Chi Siamo</a><a href="#statuto">Documenti</a><a href="organigramma.html">Organigramma</a>
    <a href="parlero.html" style="text-align:center;line-height:1.2;display:inline-flex;flex-direction:column;align-items:center;"><span style="font-weight:900;letter-spacing:.5px;">PARLER&Ograve;</span><span style="font-size:.75em;font-weight:700;color:#8a4e00;text-transform:none;letter-spacing:0;">Salotto Culturale</span></a><a href="#blog">News FB</a><a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener noreferrer">YouTube</a>
  </div>'''

if old in content:
    content = content.replace(old, new, 1)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: navbar riordinata')
else:
    print('ERRORE: stringa non trovata')
