content = open('battaglie.html', 'r', encoding='utf-8').read()
old = '  <!-- PROSSIME BATTAGLIE - placeholder -->'
new = '''  <!-- STABILICUM -->
  <div class="bat-card">
    <img src="images/pensattivo-stabilicum.jpg" alt="Stabilicum legge elettorale" class="bat-card-img" loading="lazy">
    <div class="bat-card-body">
      <div class="bat-card-num">Analisi</div>
      <span class="bat-card-tag tag-approvata">&#10003; Approvata dall&rsquo;assemblea</span>
      <h2>Stabilicum: la nuova legge elettorale spiegata ai cittadini</h2>
      <p>Da domani 31 marzo inizia l&rsquo;esame parlamentare. Come funziona, cosa cambia per chi vota.</p>
      <a href="stabilicum.html" class="btn-leggi">Leggi l&rsquo;analisi</a>
    </div>
  </div>'''

# Trova e sostituisci l'intera card coming
import re
pattern = r'  <!-- PROSSIME BATTAGLIE - placeholder -->.*?</div>\s*</div>'
result = re.sub(pattern, new, content, flags=re.DOTALL)
open('battaglie.html', 'w', encoding='utf-8').write(result)
print('Fatto!')
