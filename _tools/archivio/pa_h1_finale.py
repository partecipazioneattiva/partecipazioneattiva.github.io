from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

old = ".hero h1{margin:0 0 10px;font-size:2.1em;font-weight:900}"
new = (".hero h1{margin:0 0 16px;font-size:clamp(2.4em,7.5vw,5.2em);font-weight:900;"
       "line-height:1.02;letter-spacing:-1px;text-shadow:0 3px 14px rgba(0,0,0,.22)}")

if old in t:
    t = t.replace(old, new, 1)
    F.write_text(t, encoding="utf-8")
    print("h1 'La Mappa': clamp(2.4em - 5.2em)")
else:
    print("ATTENZIONE: css h1 non trovato")
