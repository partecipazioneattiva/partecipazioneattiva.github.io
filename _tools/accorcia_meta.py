#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Accorcia i <title> oltre 65 caratteri e le meta description oltre 160.

Perche' serve uno strumento e non una modifica a mano: la descrizione e'
scritta in QUATTRO punti della stessa pagina (meta description, og:description,
twitter:description e il campo "description" del JSON-LD). Cambiarne una sola
lascia il sito che dice due cose diverse a Google e a Facebook.

Il <title> invece si accorcia da solo: og:title e twitter:title portano il
titolo lungo senza il suffisso del movimento, e per le anteprime social va
bene cosi' (li' non c'e' nessun taglio a 65 caratteri).

    python3 _tools/accorcia_meta.py            # mostra cosa farebbe
    python3 _tools/accorcia_meta.py --applica  # scrive

I testi nuovi sono scritti a mano qui sotto, pagina per pagina: accorciare a
macchina produce titoli sgraziati.
"""
import html
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LIM_TITOLO = 65
LIM_DESCR = 160

# pagina -> (titolo nuovo | None, descrizione nuova | None)
TESTI = {
    "assemblea-noad-napoli-giugno2026.html": (
        "Assemblea NO AD a Napoli, 6 giugno 2026: PA in prima linea",
        "Resoconto dell'assemblea pubblica nazionale NO AD al Maschio Angioino: "
        "Paolo Neri, Antonio Cristiano e Luigi Spanu per Partecipazione Attiva.",
    ),
    "astensionismo-comunali2026.html": (
        "Comunali 2026: un elettore su quattro non vota più",
        "Comunali 2026: affluenza al 60,06%, quasi 5 punti in meno. I dati "
        "regione per regione e cosa significano per la democrazia.",
    ),
    "cavalleggeri-cielo-aperto.html": (
        "Cavalleggeri a cielo aperto: un museo di murales a Fuorigrotta",
        "La proposta di Partecipazione Attiva al Comune di Napoli: un museo "
        "diffuso di street art a Cavalleggeri d'Aosta, Fuorigrotta.",
    ),
    "crisi-energetica-sire.html": (
        "Crisi energetica: esiste una soluzione, si chiama SIRE",
        None,
    ),
    "crosetto-diagnosi-precoce-3dcbs.html": (
        "3D-CBS di Crosetto: due voci di PA per la diagnosi precoce",
        "Paolo Neri e Stefano Francesco Piva sostengono il progetto 3D-CBS di "
        "Dario Crosetto per la diagnosi precoce del cancro e ne chiedono la "
        "valutazione pubblica.",
    ),
    "diretta-sire.html": (
        "Convegno alla Camera sulla proposta SIRE: il resoconto",
        None,
    ),
    "importanza-sport-giovani.html": (
        "L'importanza dello sport per i giovani e per la società",
        None,
    ),
    "legge-elettorale-giusta.html": (
        "Una legge elettorale giusta: cosa vogliamo, cosa chiediamo",
        None,
    ),
    "mappa-cittadini-attivi.html": (
        "Non mancano i cittadini attivi. Manca che si vedano.",
        None,
    ),
    "pensattivo.html": (
        "PensAttivo: guarda i fatti, non la maglietta",
        None,
    ),
    "rcauto-aggiornamento-maggio2026.html": (
        "RC Auto 2026: +10%, e Napoli paga 252 euro più di Aosta",
        None,
    ),
    "rcauto-campania-mozione-maggio2026.html": (
        "RC Auto: la Campania approva la mozione contro il divario",
        "La Regione Campania chiede al Governo di eliminare le differenze "
        "tariffarie RC Auto tra Nord e Sud. La battaglia di Partecipazione Attiva.",
    ),
    "rcauto-neopatentati-giugno2026.html": (
        "Neopatentati: la polizza vale il 98% del divario Sud-Nord",
        None,
    ),
    "resoconto-assemblea-noad-napoli-6giugno2026.html": (
        "Resoconto assemblea nazionale NO AD: Napoli, 6 giugno 2026",
        None,
    ),
    "ricorso-rosatellum-cassazione-ottobre2026.html": (
        "Rosatellum in Cassazione: udienza il 29 ottobre 2026",
        None,
    ),
    "sanita-ocse-maggio2026.html": (
        "OCSE: 5,8 milioni di italiani rinunciano alle cure",
        "Il rapporto OCSE del 6 maggio 2026 sulle liste d'attesa: 2,7 milioni di "
        "rinunce nel 2023, 5,8 milioni nel 2024. Chi è povero si cura di meno.",
    ),
    # Titolo e descrizione parlavano del convegno SIRE del 9 aprile, ma la
    # pagina racconta il Congresso di Base Popolare dell'11: rifatti sul testo.
    "spanu-congresso-base-popolare.html": (
        "PA al 1° Congresso di Base Popolare: centro e proporzionale",
        "Luigi Spanu al 1° Congresso Nazionale di Base Popolare, Roma 11 aprile "
        "2026: il centro, il proporzionale e la proposta di Michele Boldrin.",
    ),
    "spanu-no-ad-autonomie-maggio2026.html": (
        "Autonomia differenziata: Spanu in due assemblee nazionali",
        "Luigi Spanu porta la voce di PA in due assemblee nazionali: online il 30 "
        "maggio con Autonomie e Ambiente, a Napoli il 6 giugno col Tavolo NO AD.",
    ),
    "stabilicum-aggiornamento-maggio2026.html": (
        "Stabilicum: soglia al 42% e 120 costituzionalisti contro",
        "Aggiornamento 16 maggio 2026: premio di maggioranza al 42%, Aula alla "
        "Camera il 26 giugno, 120 costituzionalisti: è un premierato di fatto.",
    ),
    "stabilicum-audizione-maggio2026.html": (
        "Stabilicum: Spanu audito alla Camera dei Deputati",
        None,
    ),
    "stabilicum-crepe-costituzionali-17lug2026.html": (
        "Stabilicum: le crepe costituzionali secondo Beppe Sarno",
        None,
    ),
    "stabilicum-giugno2026.html": (
        "Stabilicum: Meloni accelera, obiettivo Camera entro giugno",
        None,
    ),
    "stabilicum-nota-spanu-17lug2026.html": (
        "Spanu: le regole del voto non le scrive una parte sola",
        "La nota del portavoce nazionale Luigi Spanu dopo il sì della Camera "
        "allo Stabilicum. Il testo passa ora al Senato.",
    ),
    "stabilicum-preferenze-bocciate-14lug2026.html": (
        "Preferenze bocciate: la maggioranza battuta alla Camera",
        "La Camera boccia a scrutinio segreto l'emendamento sulle preferenze: 188 "
        "contrari, 187 favorevoli. Il resoconto e il presidio di Montecitorio.",
    ),
    # Da qui in giu' solo la descrizione: i titoli stanno gia' dentro i 65.
    "ape.html": (
        None,
        "Con APE, Partecipazione Attiva propone un'assemblea permanente di "
        "cittadini sorteggiati che obbliga le istituzioni a rispondere.",
    ),
    "chi-siamo.html": (
        None,
        "Partecipazione Attiva è un movimento civico fondato nel 2021 e ispirato "
        "alla Costituzione. Presidente Angelo Nicotra, portavoce Luigi Spanu.",
    ),
    "diritto-alla-casa.html": (
        None,
        "La proposta di Partecipazione Attiva per riconoscere l'abitazione fra i "
        "diritti fondamentali: censimento ERP, patto di responsabilità, sfitto.",
    ),
    "esserci.html": (
        None,
        "Sta per arrivare una proposta per ridare voce ai cittadini, ogni giorno "
        "e in modo permanente. Non un salvatore: noi, tutti insieme.",
    ),
    "mappa.html": (
        None,
        "La mappa dei cittadini e delle associazioni di Partecipazione Attiva: "
        "cerca chi si occupa dei temi che ti stanno a cuore, vicino a te.",
    ),
    "organigramma.html": (
        None,
        "La struttura e le persone di Partecipazione Attiva: il Comitato "
        "Direttivo, i coordinatori territoriali e i responsabili del Movimento.",
    ),
    "preferenze-stabilicum-luglio2026.html": (
        None,
        "Capolista bloccato e tre preferenze: sembra una vittoria per l'elettore. "
        "Ma nella maggior parte dei collegi la tua preferenza non sposterà nulla.",
    ),
    "perche-la-mappa.html": (
        None,
        "Divide et impera non è un modo di dire: è il metodo. Chi si occupa delle "
        "stesse cose, nella stessa città, spesso non sa nemmeno di esistere.",
    ),
    "stabilicum-aggiornamento-28maggio2026.html": (
        None,
        "Il centrodestra accelera sullo Stabilicum: Aula entro il 26 giugno 2026, "
        "premio al 42% e spaccatura interna sulle preferenze.",
    ),
}


def descr_corrente(testo):
    m = re.search(r'<meta name=["\']?description["\']?\s+content="([^"]*)"', testo)
    return m.group(1) if m else None


def titolo_corrente(testo):
    m = re.search(r"<title>(.*?)</title>", testo, re.S)
    return m.group(1) if m else None


def main():
    applica = "--applica" in sys.argv
    problemi = []
    for pagina, (titolo, descr) in sorted(TESTI.items()):
        f = BASE / pagina
        if not f.exists():
            problemi.append(f"{pagina}: non esiste")
            continue
        testo = f.read_text(encoding="utf-8")
        originale = testo

        if titolo:
            if len(titolo) > LIM_TITOLO:
                problemi.append(f"{pagina}: titolo nuovo di {len(titolo)} caratteri")
                continue
            vecchio = titolo_corrente(testo)
            if vecchio is None:
                problemi.append(f"{pagina}: nessun <title>")
                continue
            testo = testo.replace(f"<title>{vecchio}</title>",
                                  f"<title>{html.escape(titolo, quote=False)}</title>", 1)
            print(f"{pagina}\n  TITOLO {len(html.unescape(vecchio))} -> {len(titolo)}"
                  f"\n    da: {html.unescape(vecchio)}\n    a:  {titolo}")

        if descr:
            if len(descr) > LIM_DESCR:
                problemi.append(f"{pagina}: descrizione nuova di {len(descr)} caratteri")
                continue
            vecchia = descr_corrente(testo)
            if vecchia is None:
                problemi.append(f"{pagina}: nessuna meta description")
                continue
            copie = testo.count(vecchia)
            testo = testo.replace(vecchia, html.escape(descr, quote=True))
            print(f"{pagina}\n  DESCRIZIONE {len(html.unescape(vecchia))} -> {len(descr)}"
                  f"  ({copie} copie allineate)\n    da: {html.unescape(vecchia)}\n    a:  {descr}")

        if applica and testo != originale:
            f.write_text(testo, encoding="utf-8")

    if problemi:
        print("\nDA SISTEMARE:")
        for p in problemi:
            print("  -", p)
        return 1
    print("\nApplicato." if applica else "\nProva a vuoto: aggiungi --applica per scrivere.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
