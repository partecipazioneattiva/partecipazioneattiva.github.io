#!/usr/bin/env python3
"""RUOTA LE CARD DELLA HOME NELL'ARCHIVIO.

Tiene in home le N pubblicazioni più recenti (default 8) e sposta tutte le
altre in cima ad archivio.html, mantenendo l'ordine cronologico.
Le card FISSATE (data-pa-pin="1", oggi APE e WebTV) non si toccano mai.

USO:
    cd ~/Desktop/LAVORI/partecipazioneattiva
    python3 _tools/ruota_home.py            # anteprima, non scrive niente
    python3 _tools/ruota_home.py --applica  # esegue lo spostamento

FLUSSO NORMALE quando si pubblica qualcosa di nuovo:
    1. aggiungi la card nuova in cima alla lista in index.html
    2. lancia questo script con --applica
    3. la più vecchia scivola in archivio da sola

PERCHE' ESISTE: a luglio 2026 la home aveva accumulato 34 card, una lista
infinita che nessuno scorreva fino in fondo. Il problema non era estetico:
era che ogni pubblicazione andava spostata a mano e prima o poi non lo fai.
"""
import re
import shutil
import sys
from datetime import datetime

QUANTE_IN_HOME = 6
INDEX = "index.html"
ARCHIVIO = "archivio.html"

# firma delle card pubblicazione (stesso stile inline in home e archivio)
CARD = re.compile(r'<a href="([^"]+\.html)"[^>]*style="display:flex;align-items:stretch;border-radius:16px')


def trova_card(s):
    """restituisce [(inizio, fine, href, fissata)] in ordine di documento"""
    out = []
    for m in CARD.finditer(s):
        st = m.start()
        en = s.index("</a>", st) + 4
        out.append((st, en, m.group(1), 'data-pa-pin="1"' in s[st:en]))
    return out


def data_card(blocco):
    m = re.search(r"(\d{1,2}\s+[A-Za-zÀ-ÿ]+\s+20\d\d)", blocco)
    return m.group(1) if m else "senza data"


def main():
    applica = "--applica" in sys.argv
    index = open(INDEX, encoding="utf-8").read()
    archivio = open(ARCHIVIO, encoding="utf-8").read()

    card = trova_card(index)
    pubblicazioni = [c for c in card if not c[3]]
    fissate = [c for c in card if c[3]]

    print(f"in home: {len(fissate)} card fissate + {len(pubblicazioni)} pubblicazioni")

    if len(pubblicazioni) <= QUANTE_IN_HOME:
        print(f"nessuno spostamento: sono già {len(pubblicazioni)}, il limite è {QUANTE_IN_HOME}")
        return

    da_spostare = pubblicazioni[QUANTE_IN_HOME:]
    print(f"\nda spostare in archivio ({len(da_spostare)}):")
    for st, en, href, _ in da_spostare:
        print(f"  {data_card(index[st:en]):18} {href}")

    if not applica:
        print("\nanteprima soltanto. Rilancia con --applica per eseguire.")
        return

    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(INDEX, f"/tmp/index_{marca}.html")
    shutil.copy(ARCHIVIO, f"/tmp/archivio_{marca}.html")
    print(f"\nbackup in /tmp/index_{marca}.html e /tmp/archivio_{marca}.html")

    # le card da spostare sono contigue: le taglio in un colpo solo
    inizio, fine = da_spostare[0][0], da_spostare[-1][1]
    blocco = index[inizio:fine]
    nuovo_index = index[:inizio] + index[fine:]

    # le infilo in cima alla lista dell'archivio
    prima = trova_card(archivio)
    if not prima:
        sys.exit("nessuna card trovata in archivio.html: controllare la struttura")
    p = prima[0][0]
    nuovo_archivio = archivio[:p] + blocco + archivio[p:]

    open(INDEX, "w", encoding="utf-8").write(nuovo_index)
    open(ARCHIVIO, "w", encoding="utf-8").write(nuovo_archivio)

    print(f"fatto: home {len(trova_card(nuovo_index))} card, "
          f"archivio {len(trova_card(nuovo_archivio))} card")
    print("Ora verificare con un server vero (python3 -m http.server) prima di pubblicare.")


if __name__ == "__main__":
    main()
