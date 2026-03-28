with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '<span style="font-size:.65em;font-weight:500;color:#e8900a;text-transform:none;letter-spacing:0;">Salotto Culturale</span>'
new = '<span style="font-size:.75em;font-weight:700;color:#8a4e00;text-transform:none;letter-spacing:0;">Salotto Culturale</span>'

if old in content:
    content = content.replace(old, new, 1)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: Salotto Culturale aggiornato')
else:
    print('ERRORE: stringa non trovata')
