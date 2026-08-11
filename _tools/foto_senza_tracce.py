#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LE FOTO CHE RACCONTANO DOVE SEI STATO
=====================================
Ogni foto scattata con un telefono si porta dentro una scheda invisibile: il
modello dell'apparecchio, la data e l'ora esatte e — se la localizzazione era
accesa — le **coordinate del punto in cui e' stato premuto il pulsante**, con
precisione di pochi metri. Si chiamano metadati EXIF.

PERCHE' RIGUARDA PROPRIO NOI
Facebook e Instagram ripuliscono la copia pubblica di una foto quando la si
carica: da li' il rischio non passa. Ma il nostro sito **non e' Facebook**: qui
i file vengono serviti come sono. Una foto arrivata da un telefono e messa in
`images/` conserva tutto, e chiunque puo' scaricarla e leggerla — bastano venti
secondi e un sito gratuito.

Non e' teoria: e' il primo elemento che chi fa ricerche su una persona va a
guardare. Per un movimento che pubblica foto di riunioni, banchetti e case
private di chi ospita, e' una porta aperta che non serve a nessuno.

STATO ALLA PRIMA ESECUZIONE (11 agosto 2026)
128 immagini controllate, **nessuna** con coordinate, modello di apparecchio o
nome dell'autore. Il sito era gia' pulito perche' finora le immagini sono state
tutte generate o rilavorate al computer. Il rischio si presenta il giorno in cui
si pubblica una foto arrivata direttamente da un telefono: da li' in poi questo
controllo va passato prima di ogni push.

COSA TOGLIE, E COSA NON TOCCA
Toglie solo cio' che identifica persone e luoghi: coordinate, marca e modello,
numero di serie, nome dell'autore.
**Non tocca il profilo colore** (ICC): cancellare tutto alla cieca fa sbiadire
le immagini sui monitor tarati, ed e' un danno che non si vede subito.

    python3 _tools/foto_senza_tracce.py            # prova a vuoto: dice e basta
    python3 _tools/foto_senza_tracce.py --applica  # ripulisce davvero
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv
ESTENSIONI = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic")

# I campi che identificano una persona o un luogo. L'ordine e' quello con cui
# vengono mostrati nel referto.
SPIE = [
    ("GPSPosition", "coordinate del luogo"),
    ("GPSLatitude", "coordinate del luogo"),
    ("GPSLongitude", "coordinate del luogo"),
    ("Make", "marca dell'apparecchio"),
    ("Model", "modello dell'apparecchio"),
    ("SerialNumber", "numero di serie"),
    ("LensSerialNumber", "numero di serie dell'obiettivo"),
    ("OwnerName", "nome del proprietario"),
    ("Artist", "nome dell'autore"),
    ("Creator", "nome dell'autore"),
    ("By-line", "nome dell'autore"),
]

# Cosa si cancella quando si scrive davvero. Si nominano i gruppi uno per uno:
# `-all=` toglierebbe anche il profilo colore.
DA_CANCELLARE = [
    "-gps:all=",
    "-exif:make=",
    "-exif:model=",
    "-exif:serialnumber=",
    "-exif:lensserialnumber=",
    "-exif:ownername=",
    "-exif:artist=",
    "-xmp:creator=",
    "-iptc:by-line=",
]


def exiftool_c_e():
    try:
        subprocess.run(["exiftool", "-ver"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def immagini():
    fuori = {".git", "node_modules", "pagefind", "__pycache__"}
    for radice, cartelle, file in os.walk(REPO):
        cartelle[:] = [c for c in cartelle if c not in fuori]
        for f in sorted(file):
            if f.lower().endswith(ESTENSIONI):
                yield os.path.join(radice, f)


def tracce(percorso):
    """Restituisce ["coordinate del luogo: 40.85, 14.27", ...] in italiano.

    `-s -s` fa stampare a exiftool «NomeCampo: valore», una riga per campo:
    il nome serve per tradurlo, il valore per far vedere a colpo d'occhio
    quanto e' preciso il dato che stavamo per pubblicare.
    """
    etichette = dict(SPIE)
    campi = [f"-{c}" for c, _ in SPIE]
    r = subprocess.run(
        ["exiftool", "-s", "-s", "-n"] + campi + [percorso],
        capture_output=True, text=True,
    )
    trovate, gia_dette = [], set()
    for riga in r.stdout.splitlines():
        if ":" not in riga:
            continue
        campo, _, valore = riga.partition(":")
        etichetta = etichette.get(campo.strip(), campo.strip())
        valore = valore.strip()
        # coordinate spezzate in latitudine e longitudine: una riga sola basta
        chiave = (etichetta, valore)
        if etichetta in gia_dette and etichetta == "coordinate del luogo":
            continue
        if chiave in gia_dette:
            continue
        gia_dette.add(chiave)
        gia_dette.add(etichetta)
        trovate.append(f"{etichetta}: {valore}")
    return trovate


def ripulisci(percorsi):
    r = subprocess.run(
        ["exiftool"] + DA_CANCELLARE + ["-overwrite_original", "-q"] + percorsi,
        capture_output=True, text=True,
    )
    return r.returncode == 0, (r.stderr or "").strip()


def main():
    if not exiftool_c_e():
        print("  exiftool non e' installato.  brew install exiftool")
        return 1

    print("MODO:", "RIPULISCO" if APPLICA else "prova a vuoto (non scrivo niente)")

    tutte = list(immagini())
    sporche = []
    for p in tutte:
        t = tracce(p)
        if t:
            sporche.append((p, t))

    for p, t in sporche:
        rel = os.path.relpath(p, REPO)
        print(f"  📍 {rel}")
        for riga in t:
            print(f"       {riga}")

    print()
    if not sporche:
        print(f"  ✅ {len(tutte)} immagini controllate · nessuna traccia personale")
        print("     (nessuna coordinata, nessun modello di apparecchio, nessun nome)")
        return 0

    quante = (f"1 immagine su {len(tutte)} si porta"
              if len(sporche) == 1
              else f"{len(sporche)} immagini su {len(tutte)} si portano")
    print(f"  ⚠️  {quante} dietro qualcosa di personale")
    if not APPLICA:
        print("     rilancia con --applica per ripulirle")
        return 1

    ok, errore = ripulisci([p for p, _ in sporche])
    if not ok:
        print(f"  ❌ exiftool ha protestato: {errore}")
        return 1

    rimaste = [p for p, _ in sporche if tracce(p)]
    if rimaste:
        print(f"  ❌ {len(rimaste)} immagini hanno ancora tracce dopo la pulizia:")
        for p in rimaste:
            print(f"       {os.path.relpath(p, REPO)}")
        return 1
    fatte = ("1 immagine ripulita" if len(sporche) == 1
             else f"{len(sporche)} immagini ripulite")
    print(f"  ✅ {fatte} · ricontrollate una per una, ora sono pulite")
    return 0


if __name__ == "__main__":
    sys.exit(main())
