from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

old = (".hero .occhiello{font-family:Montserrat,sans-serif;font-size:1.15em;font-weight:800;"
       "text-transform:uppercase;letter-spacing:4px;color:#fff;margin:0 0 10px;"
       "text-shadow:0 1px 6px rgba(0,0,0,.25)}")
new = (".hero .occhiello{font-family:Montserrat,sans-serif;font-size:1.45em;font-weight:900;"
       "text-transform:uppercase;letter-spacing:6px;color:#fff;margin:0 0 14px;"
       "text-shadow:0 2px 10px rgba(0,0,0,.3)}")

if old in t:
    t = t.replace(old, new, 1)
    F.write_text(t, encoding="utf-8")
    print("occhiello: 1.45em, peso 900, tracking 6px")
else:
    print("ATTENZIONE: css occhiello non trovato")
