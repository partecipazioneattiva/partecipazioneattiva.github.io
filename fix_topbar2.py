# battaglie.html
with open('battaglie.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''<div class="topbar">
  <span>📧 partecipazioneattiva21@gmail.com</span>
  <span>
    <a href="https://www.facebook.com/PartecipazioneAttiva21/" target="_blank" rel="noopener noreferrer">Facebook</a>
    <a href="index.html#contatti">Contatti</a>
  </span>
</div>'''

new = '''<div class="topbar">
  <span>📧 partecipazioneattiva21@gmail.com</span>
  <div>
    <a href="https://www.facebook.com/PartecipazioneAttiva21/" target="_blank" rel="noopener noreferrer">Facebook</a>
    <a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener noreferrer">YouTube</a>
    <a href="index.html#contatti">Contatti</a>
  </div>
</div>'''

if old in content:
    content = content.replace(old, new, 1)
    with open('battaglie.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: battaglie.html')
else:
    print('ERRORE: battaglie.html')

# privacy.html
with open('privacy.html', 'r', encoding='utf-8') as f:
    content = f.read()

old2 = '''<div class="topbar">
  <span>&#128231; partecipazioneattiva21@gmail.com</span>
  <div>
    <a href="https://www.facebook.com/PartecipazioneAttiva21/" target="_blank" rel="noopener noreferrer">Facebook</a>
    <a href="index.html#contatti">Contatti</a>
  </div>
</div>'''

new2 = '''<div class="topbar">
  <span>&#128231; partecipazioneattiva21@gmail.com</span>
  <div>
    <a href="https://www.facebook.com/PartecipazioneAttiva21/" target="_blank" rel="noopener noreferrer">Facebook</a>
    <a href="https://www.youtube.com/@partecipazioneattiva" target="_blank" rel="noopener noreferrer">YouTube</a>
    <a href="index.html#contatti">Contatti</a>
  </div>
</div>'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    with open('privacy.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: privacy.html')
else:
    print('ERRORE: privacy.html')

print('FATTO')
