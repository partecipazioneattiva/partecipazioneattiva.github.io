from pathlib import Path

BASE = Path("/Users/luigia/SITO-PA")

SOST = {
 "mappa.html": [
  ("quei dati li conosce solo il direttivo.",
   "quei dati li conosce solo chi cura la mappa."),
  ("Le legge il direttivo. Se una convince, diventa un&rsquo;",
   "Le leggiamo tutte. Se una convince, diventa un&rsquo;"),
  ("Hai gi\\u00e0 tre proposte in valutazione. Aspetta che il direttivo risponda.",
   "Hai gi\\u00e0 tre proposte in valutazione. Aspetta una risposta."),
  ("<b>Proposta ricevuta.</b> La legger\\u00e0 il direttivo. Se convince, diventer\\u00e0 un\\u2019Azione pubblica e ti scriveremo.",
   "<b>Proposta ricevuta.</b> La leggeremo. Se convince, diventer\\u00e0 un\\u2019Azione pubblica e ti scriveremo."),
 ],
 "azioni.html": [
  ("I nomi degli aderenti sono noti soltanto al direttivo, perch&eacute;",
   "I nomi degli aderenti sono noti soltanto a chi cura la mappa, perch&eacute;"),
  ("La nota la legge solo il direttivo. Non viene pubblicata.",
   "La nota la legge solo chi cura la mappa. Non viene pubblicata."),
 ],
 "perche-la-mappa.html": [
  ("e poi verificata dal direttivo.",
   "e poi passa un breve controllo antiabuso."),
  ("I nomi li conosce soltanto il direttivo.",
   "I nomi li conosce soltanto chi cura la mappa."),
 ],
}

for nome, coppie in SOST.items():
    f = BASE / nome
    t = f.read_text(encoding="utf-8")
    orig = t
    for vecchio, nuovo in coppie:
        n = t.count(vecchio)
        if n == 0:
            print("  ATTENZIONE non trovato in", nome, "->", vecchio[:45])
            continue
        t = t.replace(vecchio, nuovo)
        print("  ok", nome, "(" + str(n) + ")", vecchio[:45])
    if t != orig:
        f.write_text(t, encoding="utf-8")

print("\nResidui 'direttiv':")
import subprocess
subprocess.run(["grep","-rn","-i","direttiv",
                str(BASE/"mappa.html"), str(BASE/"azioni.html"),
                str(BASE/"perche-la-mappa.html")])
