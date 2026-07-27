from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

old = "<h1>La Mappa di Partecipazione Attiva</h1>"
new = "<h1>La Mappa</h1>"

if old in t:
    t = t.replace(old, new, 1)
    F.write_text(t, encoding="utf-8")
    print("mappa.html: h1 -> 'La Mappa'")
else:
    print("ATTENZIONE: h1 non trovato")
