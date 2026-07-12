import re
from pathlib import Path

BASE = Path("/Users/luigia/SITO-PA")

# --- 1) marca la card Mappa come fissa ---
idx = BASE / "index.html"
t = idx.read_text(encoding="utf-8")
old = '<a href="mappa.html" data-pa-section="homepage-card"'
new = '<a href="mappa.html" data-pa-section="homepage-card" data-pa-pin="1"'
if 'data-pa-pin' in t:
    print("index.html: gia' presente un pin, salto")
elif old in t:
    t = t.replace(old, new, 1)
    idx.write_text(t, encoding="utf-8")
    print("index.html: card Mappa marcata come fissa")
else:
    print("ATTENZIONE: card Mappa non trovata in index.html")

# --- 2) lo script inserisce dopo le card fisse ---
sc = BASE / "aggiorna_card.py"
s = sc.read_text(encoding="utf-8")

vecchio_pat = '''    pattern = r'(<a[^>]*data-pa-section="homepage-card"[^>]*>.*?</a>)'
    match = re.search(pattern, content, re.DOTALL)'''

nuovo_pat = '''    # le card con data-pa-pin restano sempre in cima: si inserisce dopo di esse
    pattern = r'<a(?![^>]*data-pa-pin)[^>]*data-pa-section="homepage-card"[^>]*>.*?</a>'
    match = re.search(pattern, content, re.DOTALL)'''

if 'data-pa-pin' in s:
    print("aggiorna_card.py: gia' aggiornato, salto")
elif vecchio_pat in s:
    s = s.replace(vecchio_pat, nuovo_pat, 1)
    sc.write_text(s, encoding="utf-8")
    print("aggiorna_card.py: ora rispetta le card fisse")
else:
    print("ATTENZIONE: pattern non trovato in aggiorna_card.py")
