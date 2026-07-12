import json
from pathlib import Path

BASE = Path("/Users/luigia/SITO-PA")

# --- 1) card homepage ---
idx = BASE / "index.html"
t = idx.read_text(encoding="utf-8")
old = "Cittadini e associazioni sulla mappa d'Italia. Cerca per tema o competenza"
new = "Cittadini e associazioni in Italia e nel mondo. Cerca per tema o competenza"
if old in t:
    t = t.replace(old, new, 1)
    idx.write_text(t, encoding="utf-8")
    print("index.html: card aggiornata")
else:
    print("ATTENZIONE: testo card non trovato")

# --- 2) ticker (fonte di verita') ---
tj = BASE / "temi.json"
d = json.loads(tj.read_text(encoding="utf-8"))
for v in d["voci"]:
    if v.get("tema") == "LA MAPPA":
        v["testo"] = ("cittadini e associazioni in Italia e nel mondo \u2014 cerca per tema "
                      "o competenza e trova chi si batte per le stesse cose vicino a te")
        print("temi.json: voce LA MAPPA aggiornata")
tj.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
