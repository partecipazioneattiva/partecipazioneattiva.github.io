from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

old = """fetch(SB_URL+'/rest/v1/mappa_pubblica?select=*',{headers:{apikey:SB_KEY,Authorization:'Bearer '+SB_KEY}})
  .then(function(r){return r.json();})
  .then(function(d){ DATI=Array.isArray(d)?d:[]; filtra(); })"""

new = """fetch(SB_URL+'/rest/v1/mappa_pubblica?select=*',{headers:{apikey:SB_KEY,Authorization:'Bearer '+SB_KEY}})
  .then(function(r){return r.json();})
  .then(function(d){
    DATI=Array.isArray(d)?d:[]; filtra();
    var id=new URLSearchParams(location.search).get('scheda');
    if(id && DATI.filter(function(x){return x.id===id;}).length){
      mostraScheda(id); volaSu(id);
    }
  })"""

if "get('scheda')" in t:
    print("gia' presente")
elif old in t:
    t = t.replace(old, new, 1)
    F.write_text(t, encoding="utf-8")
    print("mappa.html: ora apre la scheda passata in ?scheda=<id>")
else:
    raise SystemExit("STOP: blocco fetch non trovato")
