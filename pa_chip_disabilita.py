from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

old = "['legge elettorale','sanit\\u00e0','ambiente','animali','lavoro','legale','medico-sanitaria','italiani all\\u2019estero']"
new = "['legge elettorale','sanit\\u00e0','disabilit\\u00e0','ambiente','animali','lavoro','legale','medico-sanitaria','italiani all\\u2019estero']"

if "'disabilit\\u00e0','ambiente'" in t:
    raise SystemExit("chip gia' presente")
if old not in t:
    raise SystemExit("STOP: array dei chip non trovato")

t = t.replace(old, new, 1)
F.write_text(t, encoding="utf-8")
print("mappa.html: chip 'disabilita'' aggiunto (9 chip)")
