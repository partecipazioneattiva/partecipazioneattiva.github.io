from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

old = "'sanit\\u00e0','lavoro'"
new = "'sanit\\u00e0','disabilit\\u00e0','lavoro'"

if old not in t:
    raise SystemExit("STOP: array TEMI non trovato o gia' modificato")

t = t.replace(old, new, 1)
F.write_text(t, encoding="utf-8")
print("mappa.html: tema 'disabilita'' aggiunto al form (19 temi)")
