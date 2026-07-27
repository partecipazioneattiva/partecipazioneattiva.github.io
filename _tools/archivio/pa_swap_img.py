from pathlib import Path

BASE = Path("/Users/luigia/SITO-PA")
vecchia = "images/mappa-og.jpg"
nuova = "images/cittadini-attivi.webp"

tot = 0
for nome in ("index.html", "mappa-cittadini-attivi.html"):
    F = BASE / nome
    t = F.read_text(encoding="utf-8")
    n = t.count(vecchia)
    if n:
        t = t.replace(vecchia, nuova)
        F.write_text(t, encoding="utf-8")
        print("  %s: %d occorrenze sostituite" % (nome, n))
        tot += n
    else:
        print("  %s: nessuna occorrenza" % nome)

if not tot:
    raise SystemExit("STOP: immagine vecchia non trovata, controllare a mano")
print("Fatto.")
