from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

old = "'agricoltura','sicurezza'"
new = "'agricoltura','animali','sicurezza'"

if old not in t:
    raise SystemExit("STOP: array TEMI non trovato")

t = t.replace(old, new, 1)
F.write_text(t, encoding="utf-8")
print("mappa.html: tema 'animali' aggiunto al form (18 temi)")
