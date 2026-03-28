with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Topbar desktop - dopo il link Facebook
old1 = '<a href="https://www.facebook.com/PartecipazioneAttiva21/" target="_blank" rel="noopener noreferrer">Facebook</a>\n    <a href="#contatti">Contatti</a>'
new1 = '<a href="https://www.facebook.com/PartecipazioneAttiva21/" target="_blank" rel="noopener noreferrer">Facebook</a>\n    <a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener noreferrer">YouTube</a>\n    <a href="#contatti">Contatti</a>'

if old1 in content:
    content = content.replace(old1, new1, 1)
    print('OK 1: topbar')
else:
    print('ERRORE 1: topbar non trovata')

# 2. Menu mobile - dopo il link Facebook
old2 = '<a href="#facebook" onclick="chiudi()">Facebook</a>'
new2 = '<a href="#facebook" onclick="chiudi()">Facebook</a>\n    <a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener noreferrer" onclick="chiudi()">YouTube</a>'

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('OK 2: menu mobile')
else:
    print('ERRORE 2: menu mobile non trovato')

# 3. Footer - dopo il link Facebook
old3 = '<a href="https://www.facebook.com/PartecipazioneAttiva21/" target="_blank" rel="noopener noreferrer">Facebook</a>\n'
new3 = '<a href="https://www.facebook.com/PartecipazioneAttiva21/" target="_blank" rel="noopener noreferrer">Facebook</a>\n      <a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener noreferrer">YouTube</a>\n'

if old3 in content:
    content = content.replace(old3, new3, 1)
    print('OK 3: footer')
else:
    print('ERRORE 3: footer non trovato')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('FATTO')
