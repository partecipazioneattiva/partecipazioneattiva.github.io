#!/usr/bin/env python3
"""
pa_territori.py — trasforma territori.html da pagina demotivante a CTA di reclutamento
Operazioni:
  1. 18 card "Prossimamente" → link mailto attivi "Vuoi aprire tu il primo?"
  2. CTA box esistente → aggiunge 3 passi concreti
  3. Aggiunge meta description
"""
import re, os

BASE = os.path.dirname(os.path.abspath(__file__))
fpath = os.path.join(BASE, 'territori.html')

with open(fpath, encoding='utf-8') as f:
    h = f.read()

orig = h  # per assert finale

# ── CHECK INIZIALI ──────────────────────────────────────────
assert h.count('Prossimamente') == 18, f'STOP: attese 18 card Prossimamente, trovate {h.count("Prossimamente")}'
assert 'pointer-events:none' in h, 'STOP: struttura card attesa non trovata'

# ── 1. CARD PROSSIMAMENTE → LINK MAILTO ATTIVI ──────────────
# Pattern: <a href="regione-xxx.html" style="...opacity:.65...pointer-events:none...">
#            ...bandiera... <strong ...>NomeRegione</strong>
#            <span ...>Prossimamente</span>
# Sostituzioni:
#   - opacity:.65  → opacity:1
#   - pointer-events:none  → pointer-events:auto (riattiva il click)
#   - href="regione-xxx.html" → href="mailto:..." con subject personalizzato
#   - "Prossimamente" → "Vuoi aprire tu il primo?"
#   - colore span #bbb → #9c5b00

EMAIL = 'partecipazioneattiva21@gmail.com'

def replace_card(m):
    card = m.group(0)
    # Estrai nome regione
    nome = re.search(r'<strong[^>]*>([^<]+)</strong>', card)
    if not nome:
        return card
    regione = nome.group(1).strip()
    subject = f'Gruppo PA {regione}'
    mailto = f'mailto:{EMAIL}?subject={subject.replace(" ", "%20")}'
    # Sostituisci href
    card = re.sub(r'href="regione-[^"]+\.html"', f'href="{mailto}"', card)
    # Rimuovi opacity e pointer-events
    card = card.replace('opacity:.65;', 'opacity:1;')
    card = card.replace(';opacity:.65', '')
    card = card.replace('pointer-events:none;', 'pointer-events:auto;')
    card = card.replace(';pointer-events:none', '')
    # Testo: Prossimamente → Vuoi aprire tu il primo?
    card = re.sub(
        r'(<span[^>]*color:#bbb[^>]*>)Prossimamente(</span>)',
        r'<span style="font-size:.72em;color:#9c5b00;font-weight:700">Vuoi aprire tu il primo?</span>',
        card
    )
    return card

pattern = r'<a href="regione-[^"]+\.html"[^>]*pointer-events:none[^>]*>.*?</a>'
h_new, n = re.subn(pattern, replace_card, h, flags=re.DOTALL)
assert n == 18, f'STOP: sostituite {n} card invece di 18'
assert h_new.count('Prossimamente') == 0, 'STOP: rimangono card Prossimamente'
assert h_new.count('Vuoi aprire tu il primo?') == 18, 'STOP: non tutte le card aggiornate'
assert h_new.count('pointer-events:none') == 0, 'STOP: rimangono pointer-events:none'
print(f'OK card: 18 Prossimamente → link mailto attivi (Vuoi aprire tu il primo?)')

# ── 2. CTA BOX: AGGIUNGI 3 PASSI ────────────────────────────
# Ancora: il paragrafo descrittivo della CTA box esistente
OLD_CTA_P = 'Contattaci: ti aiutiamo a costituire il gruppo territoriale e a iniziare le attivit&#224; locali.'
assert h_new.count(OLD_CTA_P) == 1, 'STOP: ancora CTA non univoca'

PASSI = '''
<div style="display:flex;gap:24px;flex-wrap:wrap;justify-content:center;margin:20px 0 24px">
<div style="flex:1;min-width:180px;text-align:center">
  <div style="font-size:1.6em;margin-bottom:6px">✉️</div>
  <strong style="color:#8a4e00;font-size:.88em">1. Scrivici</strong>
  <p style="color:#888;font-size:.80em;margin-top:4px;line-height:1.5">Mandaci un'email con la tua città e una breve presentazione</p>
</div>
<div style="flex:1;min-width:180px;text-align:center">
  <div style="font-size:1.6em;margin-bottom:6px">🤝</div>
  <strong style="color:#8a4e00;font-size:.88em">2. Ti aiutiamo</strong>
  <p style="color:#888;font-size:.80em;margin-top:4px;line-height:1.5">Ti forniamo materiali, supporto e ti mettiamo in rete con gli altri gruppi</p>
</div>
<div style="flex:1;min-width:180px;text-align:center">
  <div style="font-size:1.6em;margin-bottom:6px">🏙️</div>
  <strong style="color:#8a4e00;font-size:.88em">3. Lanciate</strong>
  <p style="color:#888;font-size:.80em;margin-top:4px;line-height:1.5">Organizzate il primo evento locale e portate le battaglie PA nel vostro territorio</p>
</div>
</div>'''

h_new = h_new.replace(
    OLD_CTA_P,
    'Tre passi per portare Partecipazione Attiva nella tua città:' + PASSI
)
assert 'Tre passi per portare' in h_new, 'STOP: CTA passi non inserita'
print('OK CTA box: 3 passi concreti aggiunti')

# ── 3. META DESCRIPTION ─────────────────────────────────────
META_DESC = '<meta name="description" content="Partecipazione Attiva è presente in Campania e Lazio. Scopri come creare un gruppo PA nella tua città e portare le nostre battaglie sul tuo territorio.">'
# Inserisci dopo <meta charset
charset = re.search(r'<meta charset[^>]+>', h_new)
assert charset, 'STOP: meta charset non trovato'
assert h_new.count(charset.group()) == 1, 'STOP: meta charset non univoco'
if 'name="description"' not in h_new:
    h_new = h_new.replace(charset.group(), charset.group() + META_DESC, 1)
    assert 'name="description"' in h_new, 'STOP: meta description non inserita'
    print('OK meta description aggiunta')
else:
    print('OK meta description già presente')

# ── SCRIVI ──────────────────────────────────────────────────
assert len(h_new) > len(orig) * 0.9, 'STOP: file risultante troppo corto'
with open(fpath, 'w', encoding='utf-8') as f:
    f.write(h_new)

print('\n--- FATTO. Ora verifica in Safari e poi PUSH ---')
