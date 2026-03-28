with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Rimuovi il duplicato nella topbar (quello con indentazione diversa)
old1 = '''    <a href="https://www.facebook.com/PartecipazioneAttiva21/" target="_blank" rel="noopener noreferrer">Facebook</a>
      <a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener noreferrer">YouTube</a>
    <a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener noreferrer">YouTube</a>
    <a href="#contatti">Contatti</a>'''

new1 = '''    <a href="https://www.facebook.com/PartecipazioneAttiva21/" target="_blank" rel="noopener noreferrer">Facebook</a>
    <a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener noreferrer">YouTube</a>
    <a href="#contatti">Contatti</a>'''

if old1 in content:
    content = content.replace(old1, new1, 1)
    print('OK 1: duplicato topbar rimosso')
else:
    print('ERRORE 1: topbar non trovata')

# 2. Aggiungi YouTube nella navbar desktop dopo il link Battaglie
old2 = '<a href="battaglie.html">Battaglie</a>\n    \n    \n  </div>'
new2 = '<a href="battaglie.html">Battaglie</a>\n    <a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener noreferrer">YouTube</a>\n  </div>'

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('OK 2: YouTube aggiunto in navbar desktop')
else:
    print('ERRORE 2: navbar desktop non trovata - cerco alternativa')
    # Prova alternativa
    old2b = '<a href="battaglie.html">Battaglie</a>\n    \n    \n  </div>'
    if old2b in content:
        content = content.replace(old2b, new2, 1)
        print('OK 2b: navbar desktop aggiornata')
    else:
        # Mostra cosa c'è dopo battaglie.html nella navbar
        idx = content.find('<a href="battaglie.html">Battaglie</a>')
        if idx > 0:
            print('Trovato Battaglie, contesto:', repr(content[idx:idx+80]))

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('FATTO')
