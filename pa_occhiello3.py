from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

# 1) CSS
css_old = ".hero h1{margin:0 0 10px;font-size:2.1em;font-weight:900}"
css_new = (".hero .occhiello{font-family:Montserrat,sans-serif;font-size:1.15em;font-weight:800;"
           "text-transform:uppercase;letter-spacing:4px;color:#fff;margin:0 0 10px;"
           "text-shadow:0 1px 6px rgba(0,0,0,.25)}\n"
           "@media(max-width:600px){.hero .occhiello{font-size:.95em;letter-spacing:2px}}\n"
           ".hero h1{margin:0 0 10px;font-size:2.1em;font-weight:900}")

if ".hero .occhiello" in t:
    print("CSS occhiello gia' presente")
elif css_old in t:
    t = t.replace(css_old, css_new, 1)
    print("CSS occhiello aggiunto")
else:
    print("ATTENZIONE: css h1 hero non trovato")

# 2) markup
h1_old = "<h1>La Mappa</h1>"
h1_new = '<div class="occhiello">Uniti per unire</div>\n    <h1>La Mappa</h1>'

if "Uniti per unire" in t:
    print("occhiello gia' nel markup")
elif h1_old in t:
    t = t.replace(h1_old, h1_new, 1)
    print("markup: 'Uniti per unire' aggiunto sopra il titolo")
else:
    print("ATTENZIONE: h1 non trovato")

F.write_text(t, encoding="utf-8")
