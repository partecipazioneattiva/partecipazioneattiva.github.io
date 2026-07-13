#!/usr/bin/env python3
# Scrive dentro mappa.html l'elenco degli iscritti come HTML STATICO.
# Motivo: le schede caricate via JS da Supabase NON sono lette dai crawler
# (Google le vede in ritardo o mai; i crawler AI non le vedono affatto).
# Da rilanciare dopo ogni approvazione in modera.py, poi push.
import json, os, sys, urllib.request, html
from pathlib import Path

BASE = Path(os.path.dirname(os.path.abspath(__file__)))
F = BASE / "mappa.html"

# chiave anon: la stessa gia' pubblica dentro mappa.html
t = F.read_text(encoding="utf-8")
import re
m_url = re.search(r"var SB_URL = '([^']+)'", t)
m_key = re.search(r"var SB_KEY = '([^']+)'", t)
if not (m_url and m_key):
    sys.exit("STOP: SB_URL/SB_KEY non trovati in mappa.html")

req = urllib.request.Request(
    m_url.group(1) + "/rest/v1/mappa_pubblica?select=*&order=regione,comune",
    headers={"apikey": m_key.group(1), "Authorization": "Bearer " + m_key.group(1)})
dati = json.loads(urllib.request.urlopen(req).read().decode())

if not dati:
    sys.exit("STOP: nessun iscritto restituito, non tocco il file")

e = lambda s: html.escape(str(s or ""), quote=True)

# ---------- elenco HTML (righe compatte, espandibili) ----------
righe = []
for r in dati:
    est = r.get("paese") and r["paese"] != "IT"
    dove = (e(r.get("comune")) + " (" + e(r.get("paese")) + ")") if est else \
           (e(r.get("comune")) + ", " + e(r.get("regione")))
    temi = r.get("temi") or []
    comp = r.get("competenze") or []
    # anteprima: primi 3 temi, il resto nel dettaglio
    prev = ", ".join(e(x) for x in temi[:3])
    if len(temi) > 3:
        prev += " +%d" % (len(temi) - 3)

    tag = "".join('<span class="tag">%s</span>' % e(x) for x in temi)
    cmp = "".join('<span class="tag cmp">%s</span>' % e(x) for x in comp)
    sito = ('<div style="margin-top:8px"><a href="%s" rel="noopener nofollow" target="_blank">%s</a></div>'
            % (e(r.get("sito_web")), e(r.get("sito_web")))) if r.get("sito_web") else ""

    righe.append(
        '<details class="voce%s">\n'
        '  <summary>\n'
        '    <span class="nome">%s</span>\n'
        '    <span class="dove">%s</span>\n'
        '    <span class="temi">%s</span>\n'
        '  </summary>\n'
        '  <div class="det">\n'
        '    <p>%s</p>\n'
        '    <div>%s%s</div>%s\n'
        '  </div>\n'
        '</details>'
        % (" est" if est else "", e(r.get("etichetta")), dove, prev,
           e(r.get("descrizione")), tag, cmp, sito))

n = len(dati)
elenco = (
'<!-- START:ELENCO -->\n'
'<section class="wrap" id="elenco">\n'
'  <h2>Chi c&rsquo;&egrave; sulla mappa</h2>\n'
'  <p class="sub">%d fra cittadini e associazioni. Clicca una riga per aprirla, oppure usa la ricerca qui sopra per filtrare per tema, competenza o luogo.</p>\n'
'  <div class="elenco" id="elenco-box">\n%s\n  </div>\n'
'  <div id="elenco-piu"><button class="btn sec" type="button" id="btn-elenco" onclick="apriElenco()">Mostra tutti (%d)</button></div>\n'
'</section>\n'
'<script>function apriElenco(){'
'  var box=document.getElementById("elenco-box"), b=document.getElementById("btn-elenco");'
'  var aperto=box.classList.toggle("tutto");'
'  b.textContent = aperto ? "Mostra meno" : "Mostra tutti (" + %d + ")";'
'  if(!aperto){ box.querySelectorAll("details.oltre[open]").forEach(function(d){d.open=false;}); '
'                document.getElementById("elenco").scrollIntoView({behavior:"smooth",block:"start"}); }'
'}</script>\n'
'<!-- END:ELENCO -->' % (n,
    "\n".join("    " + (x if i < 3 else x.replace('<details class="voce', '<details class="voce oltre', 1)).replace("\n", "\n    ")
              for i, x in enumerate(righe)),
    n, n))

# ---------- schema JSON-LD ----------
items = []
for i, r in enumerate(dati, 1):
    tipo = "Organization" if r.get("tipo") == "associazione" else "Person"
    items.append({
        "@type": "ListItem", "position": i,
        "item": {"@type": tipo, "name": r.get("etichetta"),
                 "description": r.get("descrizione"),
                 "address": {"@type": "PostalAddress",
                             "addressLocality": r.get("comune"),
                             "addressRegion": r.get("regione"),
                             "addressCountry": r.get("paese") or "IT"},
                 "knowsAbout": (r.get("temi") or []) + (r.get("competenze") or [])}})
schema = ('<!-- START:SCHEMA_MAPPA -->\n<script type="application/ld+json">%s</script>\n<!-- END:SCHEMA_MAPPA -->'
          % json.dumps({"@context": "https://schema.org", "@type": "ItemList",
                        "name": "La Mappa di Partecipazione Attiva",
                        "numberOfItems": n, "itemListElement": items},
                       ensure_ascii=False))

# ---------- CSS (una volta sola) ----------
CSS = (".elenco{margin-top:16px;border:1px solid var(--bd);border-radius:10px;overflow:hidden;background:#fff}\n"
       ".voce{border-bottom:1px solid #f0e9dc}\n"
       ".voce:last-child{border-bottom:0}\n"
       ".voce>summary{list-style:none;cursor:pointer;padding:11px 16px;display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 12px;border-left:4px solid var(--ar)}\n"
       ".voce.est>summary{border-left-color:var(--bl)}\n"
       ".voce>summary::-webkit-details-marker{display:none}\n"
       ".voce>summary:hover{background:#fff8ec}\n"
       ".voce[open]>summary{background:#fff8ec;font-weight:600}\n"
       ".voce .nome{font-family:Montserrat,sans-serif;font-weight:700;font-size:.94em;color:var(--tx)}\n"
       ".voce .dove{font-family:Montserrat,sans-serif;font-size:.78em;color:var(--ar);text-transform:uppercase;letter-spacing:.4px;font-weight:600}\n"
       ".voce.est .dove{color:var(--bl)}\n"
       ".voce .temi{font-size:.84em;color:#8a8175;margin-left:auto}\n"
       "@media(max-width:700px){.voce .temi{margin-left:0;flex-basis:100%}}\n"
       ".voce .det{padding:2px 16px 16px 20px;font-size:.9em;color:#4a443c}\n"
       ".voce .det p{margin:0 0 9px}\n"
       ".elenco .oltre{display:none}\n"
       ".elenco.tutto .oltre{display:block}\n"
       "#elenco-piu{text-align:center;margin-top:14px}\n")

if ".elenco{" not in t:
    anc = ".vuoto{text-align:center;color:#8a8175;padding:24px;font-size:.95em}"
    if anc not in t:
        sys.exit("STOP: ancora CSS non trovata")
    t = t.replace(anc, anc + "\n" + CSS.rstrip(), 1)
    print("  CSS elenco aggiunto")

# ---------- inserimento / aggiornamento ----------
def sostituisci(testo, blocco, start, end, ancora):
    if start in testo:
        i = testo.index(start)
        j = testo.index(end) + len(end)
        return testo[:i] + blocco + testo[j:]
    if ancora not in testo:
        sys.exit("STOP: ancora non trovata -> " + ancora[:40])
    return testo.replace(ancora, ancora + "\n\n" + blocco, 1)

t = sostituisci(t, elenco, "<!-- START:ELENCO -->", "<!-- END:ELENCO -->",
                '  <div id="altri"></div>\n</section>')
t = sostituisci(t, schema, "<!-- START:SCHEMA_MAPPA -->", "<!-- END:SCHEMA_MAPPA -->",
                "</head>").replace("</head>\n\n<!-- START:SCHEMA_MAPPA -->",
                                   "<!-- START:SCHEMA_MAPPA -->", 1) if False else t

# schema prima di </head>
if "<!-- START:SCHEMA_MAPPA -->" in t:
    i = t.index("<!-- START:SCHEMA_MAPPA -->")
    j = t.index("<!-- END:SCHEMA_MAPPA -->") + len("<!-- END:SCHEMA_MAPPA -->")
    t = t[:i] + schema + t[j:]
else:
    t = t.replace("</head>", schema + "\n</head>", 1)

F.write_text(t, encoding="utf-8")
print("  OK mappa.html: %d iscritti scritti nell'HTML + schema JSON-LD" % n)
print("  Ora: git add mappa.html && git commit && git push")
