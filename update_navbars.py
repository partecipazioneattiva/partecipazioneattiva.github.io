import re

# Navbar nuova per ogni pagina — riga 1 + riga 2, con voce attiva in arancio
# La voce attiva viene passata come parametro

def nuova_navbar(pagina_attiva):
    voci_riga1 = [
        ('index.html', 'Home'),
        ('napoli.html', '&#9679; Napoli'),
        ('territori.html', 'Territori'),
        ('battaglie.html', 'Battaglie'),
        ('index.html#chisiamo', 'Chi Siamo'),
        ('index.html#statuto', 'Documenti'),
        ('organigramma.html', 'Organigramma'),
    ]
    voci_riga2_parlero = '<a href="parlero.html" style="text-align:center;line-height:1.2;display:inline-flex;flex-direction:column;align-items:center;{ATTIVO_PARLERO}"><span style="font-weight:900;letter-spacing:.5px;">PARLER&Ograve;</span><span style="font-size:.75em;font-weight:700;color:#8a4e00;text-transform:none;letter-spacing:0;">Salotto Culturale</span></a>'
    
    riga1 = ''
    for href, nome in voci_riga1:
        # Determina se è la voce attiva
        attivo = ''
        if pagina_attiva == 'napoli' and href == 'napoli.html':
            attivo = ' style="color:#e8900a;font-weight:900;"'
        elif pagina_attiva == 'territori' and href == 'territori.html':
            attivo = ' style="color:#e8900a;font-weight:900;"'
        elif pagina_attiva == 'organigramma' and href == 'organigramma.html':
            attivo = ' style="color:#e8900a;font-weight:900;"'
        elif pagina_attiva == 'battaglie' and href == 'battaglie.html':
            attivo = ' style="color:#e8900a;font-weight:900;"'
        elif pagina_attiva == 'privacy':
            attivo = ''
        riga1 += f'<a href="{href}"{attivo}>{nome}</a>'

    attivo_parlero = 'color:#e8900a;font-weight:900;' if pagina_attiva == 'parlero' else ''
    parlero = voci_riga2_parlero.replace('{ATTIVO_PARLERO}', attivo_parlero)

    riga2 = parlero
    riga2 += '<a href="index.html#blog">News FB</a>'
    riga2 += '<a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener noreferrer">YouTube</a>'

    return f'''  <div class="nav-links">
    {riga1}
    {riga2}
  </div>'''

# Mappa file -> pagina attiva
pagine = {
    'napoli.html': 'napoli',
    'parlero.html': 'parlero',
    'territori.html': 'territori',
    'organigramma.html': 'organigramma',
    'battaglie.html': 'battaglie',
    'privacy.html': 'privacy',
}

for filename, pagina_attiva in pagine.items():
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Trova il blocco nav-links esistente e sostituiscilo
    pattern = r'  <div class="nav-links">.*?</div>'
    nuovo = nuova_navbar(pagina_attiva)
    new_content, n = re.subn(pattern, nuovo, content, count=1, flags=re.DOTALL)

    if n == 0:
        print(f'ERRORE: nav-links non trovato in {filename}')
    else:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'OK: {filename}')

print('FATTO')
