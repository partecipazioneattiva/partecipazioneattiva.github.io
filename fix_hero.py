with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Il problema: lo <script> RSS è fuori dalla colonna sinistra (manca </div> prima di <script>)
# e la colonna destra non ha il suo <div> di apertura.
# Dobbiamo:
# 1. Chiudere la colonna sinistra PRIMA dello script (aggiungere </div> dopo hero-notizia)
# 2. Aprire la colonna destra DOPO lo script con <div>

old = '''      </div>
    </div>

<script>
async function loadHeroNews() {'''

new = '''      </div>
    </div>
    </div>

<script>
async function loadHeroNews() {'''

if old not in content:
    print('ERRORE: stringa 1 non trovata')
else:
    content = content.replace(old, new, 1)
    print('OK: chiusura colonna sinistra aggiunta')

# Ora aggiungiamo il <div> di apertura colonna destra dopo loadHeroNews();
old2 = '''loadHeroNews();
</script>
    <div style="background:rgba(255,255,255,0.10)'''

new2 = '''loadHeroNews();
</script>
    <div>
    <div style="background:rgba(255,255,255,0.10)'''

if old2 not in content:
    print('ERRORE: stringa 2 non trovata')
else:
    content = content.replace(old2, new2, 1)
    print('OK: apertura colonna destra aggiunta')

# Ora dobbiamo chiudere la colonna destra prima di </div></section>
# La colonna destra si chiude dopo </div> della griglia delle card
old3 = '''    </div>
  </div>
</section>



<section id="napoli"'''

new3 = '''    </div>
    </div>
  </div>
</section>



<section id="napoli"'''

if old3 not in content:
    print('ERRORE: stringa 3 non trovata')
else:
    content = content.replace(old3, new3, 1)
    print('OK: chiusura colonna destra aggiunta')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('FATTO')
