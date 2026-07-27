import re
from pathlib import Path

BASE = Path("/Users/luigia/SITO-PA")
AUTO_SLASH = "os.path.dirname(os.path.abspath(__file__)) + '/'"
AUTO_NUDO  = "os.path.dirname(os.path.abspath(__file__))"

# riga tipo:  BASE = '/Users/luigia/SITO-PA/'   oppure   base = "/Users/luigia/SITO-PA"
RIGA = re.compile(r"""^(\s*)(BASE|base)\s*=\s*['"](/Users/(?:luigia|osxssd)/[^'"]*)['"]\s*$""", re.M)

fatti, saltati = [], []

for f in sorted(BASE.glob("*.py")):
    if f.name in ("pubblica_articolo.py", "pa_path_portabili.py"):
        continue
    t = f.read_text(encoding="utf-8")
    m = RIGA.search(t)
    if not m:
        continue

    var, path_vecchio = m.group(2), m.group(3)
    auto = AUTO_SLASH if path_vecchio.endswith("/") else AUTO_NUDO
    nuovo = f"{m.group(1)}{var} = {auto}"

    # lo script deve importare os
    if not re.search(r"^\s*import\s+.*\bos\b", t, re.M):
        t = t.replace(m.group(0), nuovo, 1)
        t = nuovo.join(["", ""])  # placeholder, sostituito sotto
        t = f.read_text(encoding="utf-8")
        t = RIGA.sub(nuovo, t, count=1)
        t = "import os\n" + t if not t.startswith("#!") else \
            t.replace("\n", "\nimport os\n", 1)
        saltati.append((f.name, "aggiunto import os"))
    else:
        t = RIGA.sub(nuovo, t, count=1)

    f.write_text(t, encoding="utf-8")
    fatti.append(f.name)

print("SISTEMATI (%d):" % len(fatti))
for n in fatti:
    print("  -", n)
if saltati:
    print("\nNOTA:")
    for n, msg in saltati:
        print("  -", n, "->", msg)
