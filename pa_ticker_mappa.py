import json
from pathlib import Path

F = Path("/Users/luigia/SITO-PA/temi.json")
d = json.loads(F.read_text(encoding="utf-8"))
voci = d.get("voci", [])

nuova = {
    "emoji": "\U0001F5FA\uFE0F",
    "tema": "LA MAPPA",
    "testo": "cittadini e associazioni sulla mappa d\u2019Italia \u2014 cerca per tema o competenza e trova chi si batte per le stesse cose vicino a te"
}

if any(v.get("tema") == "LA MAPPA" for v in voci):
    print("voce gia' presente, salto")
else:
    voci.insert(0, nuova)
    d["voci"] = voci
    F.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print("temi.json: voce LA MAPPA aggiunta in cima")

print("Voci attuali:")
for v in d["voci"]:
    print(" -", v["tema"])
