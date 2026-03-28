old_link = 'https://docs.google.com/forms/d/e/1FAIpQLSe1_6wKpGKMCnlCyo-yU1W6IuXHNJMESnzRDUbg92qjDE-6SQ/viewform'
new_link = 'https://docs.google.com/forms/d/e/1FAIpQLSdUJHaPB9o6gA7TXHNLNgsKcftZjwCsjepZ3r_C9TH2ODsr3A/viewform'

pagine = ['index.html', 'battaglie.html']

for filename in pagine:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    n = content.count(old_link)
    if n > 0:
        content = content.replace(old_link, new_link)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'OK: {filename} ({n} sostituzioni)')
    else:
        print(f'ERRORE: link non trovato in {filename}')

print('FATTO')
