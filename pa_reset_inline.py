from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

if 'id="qx"' in t:
    raise SystemExit("gia' fatto")

# --- 1) CSS: wrapper + bottone X dentro la barra ---
css_old = "#q:focus{border-color:var(--ar)}"
css_new = ("#q:focus{border-color:var(--ar)}\n"
".qbox{position:relative}\n"
"#q{padding-right:52px}\n"
"#qx{position:absolute;right:8px;top:50%;transform:translateY(-50%);display:none;"
"width:34px;height:34px;border:0;border-radius:50%;background:#f2ede4;color:#6b6255;"
"font-size:1.05em;line-height:1;cursor:pointer;align-items:center;justify-content:center}\n"
"#qx.on{display:flex}\n"
"#qx:hover{background:#6b6255;color:#fff}")

if css_old in t:
    t = t.replace(css_old, css_new, 1)

# --- 2) markup: avvolgo l'input ---
old = '<input id="q" type="text" placeholder="Cerca un tema, una competenza, un luogo..." autocomplete="off">'
new = ('<div class="qbox">\n'
       '    <input id="q" type="text" placeholder="Cerca un tema, una competenza, un luogo..." autocomplete="off">\n'
       '    <button id="qx" type="button" title="Azzera la ricerca" aria-label="Azzera la ricerca">&#10005;</button>\n'
       '  </div>')

if old not in t:
    raise SystemExit("STOP: input di ricerca non trovato")
t = t.replace(old, new, 1)

# --- 3) tolgo il chip azzera (ora e' dentro la barra) ---
chip_old = ("\n  + '<span class=\"chip azz\" onclick=\"document.getElementById(\\'q\\').value=\\'\\';filtra()\">"
            "\\u2715 azzera ricerca</span>';")
if chip_old in t:
    t = t.replace(chip_old, ";", 1)
    print("chip 'azzera ricerca' rimosso (ora e' nella barra)")

# --- 4) JS: mostra/nascondi la X ---
old_js = "document.getElementById('q').oninput=filtra;"
new_js = ("""function aggiornaX(){
  document.getElementById('qx').classList.toggle('on', document.getElementById('q').value.trim() !== '');
}
document.getElementById('q').oninput=function(){ filtra(); aggiornaX(); };
document.getElementById('qx').onclick=function(){
  var q=document.getElementById('q');
  q.value=''; filtra(); aggiornaX(); q.focus();
};""")

if old_js not in t:
    raise SystemExit("STOP: handler oninput non trovato")
t = t.replace(old_js, new_js, 1)

# il click sui chip deve far comparire la X
t = t.replace("value=\\''+t+'\\';filtra()", "value=\\''+t+'\\';filtra();aggiornaX()", 1)

F.write_text(t, encoding="utf-8")
print("mappa.html: X di reset dentro la barra, compare solo quando serve")
