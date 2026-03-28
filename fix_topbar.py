pagine = ['napoli.html', 'parlero.html', 'territori.html', 'organigramma.html', 'battaglie.html', 'privacy.html']

old_topbar = '''<div class="topbar">
  <span>📧 partecipazioneattiva21@gmail.com</span>
  <div>
    <a href="https://www.facebook.com/PartecipazioneAttiva21/" target="_blank">Facebook</a>
    <a href="index.html">Home</a>
  </div>
</div>'''

new_topbar = '''<div class="topbar">
  <span>📧 partecipazioneattiva21@gmail.com</span>
  <div>
    <a href="https://www.facebook.com/PartecipazioneAttiva21/" target="_blank" rel="noopener noreferrer">Facebook</a>
    <a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener noreferrer">YouTube</a>
    <a href="index.html#contatti">Contatti</a>
  </div>
</div>'''

for filename in pagine:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_topbar in content:
        content = content.replace(old_topbar, new_topbar, 1)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'OK: {filename}')
    else:
        print(f'ERRORE: topbar non trovata in {filename}')

print('FATTO')
