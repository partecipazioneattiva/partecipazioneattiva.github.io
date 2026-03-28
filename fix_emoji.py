file = 'index.html'

with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

old = '<div style="font-size:2em;margin-bottom:12px;">🆓</div>'
new = '<div style="font-size:2em;margin-bottom:12px;">🎁</div>'

if old in content:
    content = content.replace(old, new)
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: emoji aggiornata')
else:
    print('ERRORE: emoji non trovata')
