from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

old = "+ '<span class=\"chip\" onclick=\"document.getElementById(\\'q\\').value=\\'\\';filtra()\">azzera</span>';"
new = ("+ '<span class=\"chip azz\" onclick=\"document.getElementById(\\'q\\').value=\\'\\';filtra()\">"
       "\\u2715 azzera ricerca</span>';")

if "azzera ricerca" in t:
    raise SystemExit("gia' fatto")
if old not in t:
    raise SystemExit("STOP: chip azzera non trovato")

t = t.replace(old, new, 1)

# stile distinto: grigio, staccato dagli altri
css_old = ".chip:hover,.chip.on{background:var(--ar);color:#fff;border-color:var(--ar)}"
css_new = (".chip:hover,.chip.on{background:var(--ar);color:#fff;border-color:var(--ar)}\n"
           ".chip.azz{background:#f2ede4;color:#6b6255;border-color:#ddd4c4;margin-left:10px}\n"
           ".chip.azz:hover{background:#6b6255;color:#fff;border-color:#6b6255}")

if css_old in t:
    t = t.replace(css_old, css_new, 1)

F.write_text(t, encoding="utf-8")
print("mappa.html: chip -> '✕ azzera ricerca', in grigio e staccato")
