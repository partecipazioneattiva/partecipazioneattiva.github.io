pagine = ['parlero.html', 'napoli.html', 'territori.html', 'organigramma.html']

old = 'href="mailto:partecipazioneattiva21@gmail.com?subject=Richiesta di Iscrizione" class="btn-iscr"'
new = 'href="https://docs.google.com/forms/d/e/1FAIpQLSdUJHaPB9o6gA7TXHNLNgsKcftZjwCsjepZ3r_C9TH2ODsr3A/viewform" target="_blank" rel="noopener noreferrer" class="btn-iscr"'

for filename in pagine:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    if old in content:
        content = content.replace(old, new)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'OK: {filename}')
    else:
        print(f'SKIP: {filename} (link non trovato)')

print('FATTO')
