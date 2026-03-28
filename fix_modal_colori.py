import os

files = ['index.html','napoli.html','parlero.html','territori.html','organigramma.html','battaglie.html','privacy.html']

old = '<div style="font-size:.8em;color:#444;line-height:1.8;">'
new = '<div style="font-size:.82em;color:#222;line-height:1.9;font-weight:500;">'

old2 = '<p style="color:#666;font-size:.85em;text-align:center;margin-bottom:24px;">Ogni contributo ci aiuta a portare avanti le nostre battaglie.</p>'
new2 = '<p style="color:#333;font-size:.85em;text-align:center;margin-bottom:24px;">Ogni contributo ci aiuta a portare avanti le nostre battaglie.</p>'

old3 = '<p style="font-size:.72em;color:#999;text-align:center;">Causale: Iscrizione/Rinnovo/Donazione progetto politico</p>'
new3 = '<p style="font-size:.75em;color:#555;text-align:center;font-weight:600;">Causale: Iscrizione/Rinnovo/Donazione progetto politico</p>'

for f in files:
    if not os.path.exists(f):
        print(f'SKIP: {f} non trovato')
        continue
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    modified = False
    if old in content:
        content = content.replace(old, new)
        modified = True
    if old2 in content:
        content = content.replace(old2, new2)
        modified = True
    if old3 in content:
        content = content.replace(old3, new3)
        modified = True
    if modified:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        print(f'OK: {f}')
    else:
        print(f'NESSUNA MODIFICA: {f}')

print('FATTO')
