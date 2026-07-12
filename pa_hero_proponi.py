from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
h = F.read_text(encoding="utf-8")

if 'id="proponi"' not in h:
    assert h.count('class="propbox"') == 1, "propbox non univoco"
    h = h.replace('class="propbox"', 'id="proponi" class="propbox"', 1)

btn = '      <a class="bhero ghost" href="#proponi">Proponi un&rsquo;idea</a>\n'
anchor = '      <a class="bhero ghost" href="perche-la-mappa.html">Perch&eacute; una mappa</a>\n'
if 'href="#proponi"' not in h:
    assert anchor in h, "hero non trovato"
    h = h.replace(anchor, btn + anchor, 1)

js = '<script>\n(function(){\n  function apri(){\n    var f=document.querySelector(".propform");\n    if(f) f.classList.add("on");\n  }\n  document.querySelectorAll(\'a[href="#proponi"]\').forEach(function(a){\n    a.addEventListener("click",function(){setTimeout(apri,50);});\n  });\n  if(location.hash==="#proponi") setTimeout(apri,80);\n})();\n</script>\n'

if 'href=\\"#proponi\\"' not in h and 'setTimeout(apri' not in h:
    h = h.replace("</body>", js + "</body>", 1)

F.write_text(h, encoding="utf-8")
print("OK - mappa.html aggiornata")
