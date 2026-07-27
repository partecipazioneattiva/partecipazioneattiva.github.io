from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

# occhiello piu' grande e leggibile
old = (".hero .occhiello{font-family:Montserrat,sans-serif;font-size:.8em;font-weight:800;"
       "text-transform:uppercase;letter-spacing:3px;color:#ffe0a0;margin:0 0 8px}")
new = (".hero .occhiello{font-family:Montserrat,sans-serif;font-size:1.15em;font-weight:800;"
       "text-transform:uppercase;letter-spacing:4px;color:#fff;margin:0 0 10px;"
       "text-shadow:0 1px 6px rgba(0,0,0,.25)}\n"
       "@media(max-width:600px){.hero .occhiello{font-size:.95em;letter-spacing:2px}}")

if old in t:
    t = t.replace(old, new, 1)
    print("occhiello ingrandito (1.15em, bianco pieno)")
else:
    print("ATTENZIONE: css occhiello non trovato")

# bottoni leggermente piu' piccoli
b_old = ("padding:12px 28px;border-radius:50px;font-family:Montserrat,sans-serif;"
         "font-weight:800;font-size:.92em}")
b_new = ("padding:10px 22px;border-radius:50px;font-family:Montserrat,sans-serif;"
         "font-weight:800;font-size:.85em}")

if b_old in t:
    t = t.replace(b_old, b_new, 1)
    print("bottoni hero ridotti")
else:
    print("ATTENZIONE: css bottoni non trovato")

F.write_text(t, encoding="utf-8")
