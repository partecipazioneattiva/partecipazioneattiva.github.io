#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
«E ADESSO?» IN FONDO AGLI ARTICOLI
==================================
Fase 3.1 del piano esecutivo — il miglior rapporto fatica/risultato.

IL PROBLEMA, CONTATO l'8 agosto 2026: 37 pagine su 64 finiscono con
«Hai trovato utile questo articolo? Condividilo» e tre bottoni social. Punto.
Chi ha appena letto un'analisi sulla legge elettorale non ha modo di sapere
che esiste una proposta collegata, una battaglia in corso, o come dire la sua.
L'articolo e' un vicolo cieco.

COSA FA: aggiunge in coda un blocco con TRE passi, scelti in base a di cosa
parla l'articolo — approfondisci · la battaglia collegata · partecipa.
Mai un rimando alla pagina stessa.

Le famiglie tematiche sono decise qui sotto, a mano. Non si indovinano: un
«e adesso?» che manda fuori tema e' peggio di nessun «e adesso?».

    python3 _tools/e_adesso.py            # prova a vuoto
    python3 _tools/e_adesso.py --applica
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICA = "--applica" in sys.argv

# ── i passi possibili ──────────────────────────────────────────────────────
P = {
    "stabilicum":  ("stabilicum.html", "Cos'è lo Stabilicum, spiegato"),
    "legge":       ("legge-elettorale-giusta.html", "La legge elettorale che vogliamo"),
    "rcauto":      ("rcauto.html", "La battaglia sull'RC Auto"),
    "sanita":      ("sanitapubblica.html", "La battaglia sulla sanità pubblica"),
    "ape":         ("ape.html", "La proposta APE"),
    "reteape":     ("rete-ape.html", "La Rete per l'APE"),
    "battaglie":   ("battaglie.html", "Tutte le nostre battaglie"),
    "azioni":      ("azioni.html", "Le azioni in corso"),
    "proposte":    ("proposte.html", "Proponi la tua idea"),
    "mappa":       ("mappa.html", "Entra nella Mappa"),
    "napoli":      ("napoli.html", "Partecipazione Attiva a Napoli"),
    "territori":   ("territori.html", "Dove siamo, sul territorio"),
    "webtv":       ("webtv.html", "Guarda la WebTV"),
    "chisiamo":    ("chi-siamo.html", "Chi siamo"),
}

# ── quale famiglia per quale articolo ──────────────────────────────────────
FAMIGLIE = [
    (r"^stabilicum|^preferenze-stabilicum|^ricorso-rosatellum|^legge-elettorale-giusta",
     ["stabilicum", "legge", "proposte"]),
    (r"^rcauto",                    ["rcauto", "battaglie", "proposte"]),
    (r"sanita|crosetto",            ["sanita", "battaglie", "proposte"]),
    (r"^ape\.|^rete-ape|^mappa-cittadini", ["ape", "mappa", "proposte"]),
    (r"noad|autonomi",              ["battaglie", "azioni", "proposte"]),
    (r"sire|crisi-energetica",      ["proposte", "battaglie", "mappa"]),
    (r"^cavalleggeri",              ["napoli", "territori", "mappa"]),
    (r"^diritto-alla-casa|^importanza-sport", ["battaglie", "proposte", "mappa"]),
    (r"^astensionismo",             ["legge", "mappa", "proposte"]),
    (r"^pensattivo|^settembre-2026", ["webtv", "battaglie", "mappa"]),
    (r"^spanu-congresso|^curriculum|^notte-democrazia|^diretta-|^assemblea-|^resoconto-",
     ["chisiamo", "azioni", "mappa"]),
]
DEFAULT = ["battaglie", "proposte", "mappa"]

ANCORA = "trovato utile"
MARCA = "pa-e-adesso"


def passi_per(f):
    for regola, passi in FAMIGLIE:
        if re.search(regola, f):
            scelti = passi
            break
    else:
        scelti = DEFAULT
    # mai un rimando a se stessa
    return [k for k in scelti if P[k][0] != f]


def blocco(passi):
    link = "".join(
        f'<a href="{P[k][0]}">{P[k][1]}</a>' for k in passi
    )
    return (f'<div class="{MARCA}" data-pagefind-ignore>'
            f'<div class="{MARCA}-tit">E adesso?</div>'
            f'<div class="{MARCA}-link">{link}</div></div>')


def main():
    print("MODO:", "SCRIVO" if APPLICA else "prova a vuoto (non scrivo niente)")
    fatte = saltate = 0
    for f in sorted(x for x in os.listdir(REPO) if x.endswith(".html")):
        if f == "template.html":
            continue
        p = os.path.join(REPO, f)
        d = open(p, encoding="utf-8").read()
        if ANCORA not in d:
            continue
        if MARCA in d:
            saltate += 1
            continue
        passi = passi_per(f)
        if not passi:
            print(f"  ⚠️  {f}: nessun passo sensato, salto")
            continue
        # il blocco va PRIMA dell'invito a condividere: il passo successivo
        # conta piu' della condivisione
        i = d.find(ANCORA)
        i = d.rfind("<", 0, i)
        # risalgo al contenitore del paragrafo
        j = d.rfind("<div", 0, i)
        punto = j if j != -1 and (i - j) < 400 else i
        nuovo = d[:punto] + blocco(passi) + d[punto:]
        fatte += 1
        print(f"  ✏️  {f[:44]:44} → " + " · ".join(P[k][1][:26] for k in passi))
        if APPLICA:
            open(p, "w", encoding="utf-8").write(nuovo)
    print(f"\n  {fatte} articoli · {saltate} gia' fatti")
    if not APPLICA:
        print("  (rilancia con --applica per scrivere)")


if __name__ == "__main__":
    main()
