from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

old = (".hero h1{margin:0 0 14px;font-size:3.6em;font-weight:900;line-height:1.05}\n"
       "@media(max-width:600px){.hero h1{font-size:2.6em}}")
new = (".hero h1{margin:0 0 16px;font-size:clamp(2.4em,7.5vw,5.2em);font-weight:900;"
       "line-height:1.02;letter-spacing:-1px;text-shadow:0 3px 14px rgba(0,0,0,.22)}")

if old in t:
    t = t.replace(old, new, 1)
    F.write_text(t, encoding="utf-8")
    print("h1: clamp(2.4em - 5.2em), si adatta allo schermo")
else:
    print("ATTENZIONE: css h1 non trovato (lo script precedente e' stato eseguito?)")
