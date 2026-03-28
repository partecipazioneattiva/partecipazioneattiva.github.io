with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Rimuovi Parlerò dalla riga 2
old1 = '    <a href="#statuto">Documenti</a>\n    <a href="parlero.html">Parler&ograve;</a><a href="battaglie.html">Battaglie</a>'
new1 = '    <a href="#statuto">Documenti</a>\n    <a href="battaglie.html">Battaglie</a>'

if old1 in content:
    content = content.replace(old1, new1, 1)
    print('OK 1: Parlerò rimosso da riga 2')
else:
    print('ERRORE 1: riga 2 non trovata')

# Aggiungi Parlerò con sottotitolo nella riga 1, dopo Chi Siamo
old2 = '<a href="territori.html">Territori</a><a href="organigramma.html">Organigramma</a><a href="#chisiamo">Chi Siamo</a>'
new2 = '<a href="territori.html">Territori</a><a href="organigramma.html">Organigramma</a><a href="#chisiamo">Chi Siamo</a><a href="parlero.html" style="text-align:center;line-height:1.2;display:inline-flex;flex-direction:column;align-items:center;"><span style="font-weight:900;letter-spacing:.5px;">PARLER&Ograve;</span><span style="font-size:.65em;font-weight:500;color:#e8900a;text-transform:none;letter-spacing:0;">Salotto Culturale</span></a>'

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('OK 2: Parlerò aggiunto in riga 1 con sottotitolo')
else:
    print('ERRORE 2: riga 1 non trovata')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('FATTO')
