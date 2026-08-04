#!/usr/bin/env python3
"""Scrive il prompt del manifesto elettorale di un candidato, gia' pronto da
incollare su Gemini / Nano Banana (aistudio.google.com).

    python3 _tools/crea_prompt_manifesto.py --candidato rosa
    python3 _tools/crea_prompt_manifesto.py --elenco

Le impostazioni delle persone NON stanno qui dentro: questo repository e'
pubblico e quelle sono descrizioni fisiche di persone reali. Stanno in
    ~/Desktop/GEMINI LAVORI/candidati_manifesto.json
accanto alle foto, e si sovrascrive il percorso con --dati.

⛔ LA REGOLA CHE QUESTO SCRIPT ESISTE PER PROTEGGERE
Nelle Municipalita' di Napoli l'istruzione di voto dipende dal RUOLO, e
sbagliarla costa voti veri:
  - Presidente  -> si vota barrando il SIMBOLO. Un segno sul solo nome del
                   candidato Presidente vale come voto a lui e NON alla lista
                   (art. 3 del Regolamento delle Municipalita'), e i seggi li
                   prende la lista: senza seggio della lista, il Presidente non
                   eletto non entra.
  - Consigliere -> serve la PREFERENZA SCRITTA: barra il simbolo e scrivi il
                   cognome. Senza il cognome scritto, zero preferenze.
Qui l'istruzione si deriva dal campo 'ruolo': non si scrive piu' a mano.
"""
import argparse
import json
import os
import sys

DATI = "~/Desktop/GEMINI LAVORI/candidati_manifesto.json"

# L'istruzione di voto, derivata dal ruolo. Non si tocca senza rileggere
# l'art. 3 del Regolamento delle Municipalita' di Napoli.
VOTO = {
    "presidente": ('"BARRA IL SIMBOLO" e "sulla scheda della Municipalita\'"',
                   "due righe piccole"),
    "consigliere": ('"BARRA IL SIMBOLO" e "e scrivi {cognome} sulla scheda"',
                    "due righe piccole, la seconda un poco piu' marcata della prima"),
}


def prompt(c, com, senza_simbolo=False):
    f = c["genere"] == "f"
    art = "la persona di cui"
    migliorare = "migliorarla" if f else "migliorarlo"
    pr = "la" if f else "lo"          # pronome, per le concordanze
    riga7, modo7 = VOTO[c["ruolo"]]
    riga7 = riga7.format(cognome=c["cognome"])

    # ⛔ Il logo NON si fa disegnare al generatore quando si puo' evitare: lo
    #    ridisegna e ci traccia sopra una X che mangia le lettere. Con
    #    --senza-simbolo l'angolo resta vuoto e il simbolo VERO lo incolla
    #    _tools/sostituisci_simbolo.py. Provato il 4 agosto 2026: rattoppare
    #    un simbolo gia' disegnato su un fondo eterogeneo lascia un alone.
    if senza_simbolo:
        quante, ruoli = "cinque", "due"
        riga_b = ""
        # ⭐ Lo spazio si lascia CIRCOLARE, non quadrato (Fernando, 4 agosto
        #    2026): il logo e' un disco, e un riquadro quadrato lascia sempre
        #    quattro angoli da rifilare a mano dopo l'incollaggio.
        blocco_simbolo = (
            "In basso a sinistra, sopra la figura, lascia una ZONA VUOTA "
            "CIRCOLARE, un disco largo circa un terzo della larghezza del "
            "manifesto, alla stessa altezza delle due righe del punto 7. Dentro "
            "quel cerchio non c'e' assolutamente nulla: solo il fondo pergamena, "
            "liscio e uniforme, senza bordi, senza cornice, senza ombra e senza "
            "contorno che ne segni il perimetro. Non disegnare nessun logo, "
            "nessun simbolo, nessuna X, nessun segnaposto: quello spazio lo "
            "riempio io dopo, e qualunque cosa tu ci metta va cancellata.")
    else:
        quante, ruoli = "sei", "tre"
        riga_b = ("IMMAGINE B - il logo dell'associazione: riproducilo "
                  "fedelmente, senza ridisegnarlo e senza cambiarne i colori.\n")
        blocco_simbolo = (
            "In basso a sinistra, sopra la figura, il logo dell'immagine B "
            "riprodotto intero e perfettamente leggibile. Sopra il logo, due soli "
            "tratti sottili incrociati a formare una X, tracciati a mano con un "
            "pennarello rosso semitrasparente, come il segno che l'elettore fa "
            "sulla scheda.\nLa X non deve coprire nessuna lettera: le parole "
            "\"PARTECIPAZIONE\" e \"ATTIVA\" devono restare leggibili per intero. "
            "I tratti sono sottili, passano sopra la parte centrale del disegno e "
            "non sopra le scritte.\nIl logo sta alla stessa altezza delle due "
            "righe del punto 7.")

    # ⛔ I nomi propri si compitano lettera per lettera: e' l'unico modo per cui
    #    il generatore non li reinventa. Su Luigi aveva scritto "Bariianoraina
    #    ungnoli" al posto di "Bagnoli"; sul logo "PA TECIPAZI NE".
    propri = [c["cognome"]] + [w for w in c["territorio"].replace("e ", "").split()
                               if len(w) > 3]
    compitato = "; ".join(f"{w} si scrive {'-'.join(w.upper())}" for w in propri)

    return f"""Ti allego {quante} immagini, con {ruoli} ruoli diversi.
IMMAGINI A1, A2, A3, A4 - quattro fotografie della stessa persona, {c['nome'].title()}, {art} sto preparando il materiale e di cui ho il consenso: sono la fonte del suo ritratto. Usale tutte e quattro insieme per ricostruire il viso, non solo la prima.
{riga_b}IMMAGINE C - uno schema di impaginazione muto: i rettangoli grigi indicano soltanto dove va ogni elemento e quanto e' grande, e corrispondono nell'ordine dall'alto in basso all'elenco che trovi sotto. Non riprodurre i rettangoli, non riprodurne i colori, non scrivere parole che non siano nell'elenco.

Canvas: {com['canvas']}, risoluzione massima disponibile.

Crea un manifesto elettorale italiano da affissione, di quelli che si leggono a trenta metri di distanza: pochissimi elementi, molto grandi, ad alto contrasto.

IMPAGINAZIONE D'INSIEME: un fondo solo, chiaro e caldo, colore pergamena con una velatura dorata. {c['nome'].title()} e' ritagliat{'a' if f else 'o'} sul fondo, occupa la meta' sinistra e va da sopra fino al bordo inferiore, senza cornici e senza fasce che dividano la tela. Tutto il testo sta nella meta' destra, allineato a sinistra, e non copre mai il viso.

IL VOLTO E' L'ELEMENTO DOMINANTE. Ritrai {c['nome'].title()} esattamente come appare nelle fotografie A1-A4, senza {migliorare} in nessun modo. Il criterio non e' che sia un bel ritratto: e' che chi {pr} conosce {pr} riconosca per strada.
Riporta fedelmente questi tratti, che nelle fotografie ci sono e che i ritratti generati tendono a cancellare: {c['tratti']}
{c['espressione']}
E' un ritratto posato per un manifesto, quindi la persona e' curata: capelli pettinati e in ordine, ma con il loro volume e il loro movimento naturale, non appiattiti e non ridisegnati.
{c['divieti']}
Inquadratura a mezzo busto, frontale, sguardo dritto nell'obiettivo. {c['abbigliamento']} {c['da_togliere']} Luce calda e frontale sul volto, nessuna ombra dura sugli occhi.

⛔ IL TESTO DEL MANIFESTO — da riprodurre ALLA LETTERA
Quelle che seguono sono le UNICHE parole che compaiono nel manifesto. Ogni riga va copiata carattere per carattere, esattamente come e' scritta qui, una volta sola. Il testo e' in italiano, in caratteri lapidari senza grazie, molto marcati, colore bruno scurissimo, e le righe stanno in quest'ordine dall'alto in basso:

1. in alto, grande: "{com['elezione']}"
2. subito sotto, piu' grande ancora e nel rosso caldo di accento: "{com['data']}"
3. piu' in basso, staccato e ben visibile: "{com['slogan']}"
4. subito sotto, di corpo medio: "{c['nome']}"
5. sotto, la riga piu' grande di tutto il manifesto dopo il volto: "{c['cognome']}"
6. piu' piccolo: "{c['carica']} · {c['territorio']}"
7. in fondo, {modo7}: {riga7}

{blocco_simbolo}

Sul bordo sinistro della tela, scritta in verticale e nel corpo piu' piccolo di tutto il manifesto: "Committente responsabile: {com['committente']}".

⛔ COME SI COPIA IL TESTO — la parte in cui si sbaglia sempre
Non tradurre, non abbreviare, non spezzare le parole con trattini, non ripeterle, non aggiungere articoli, preposizioni, titoli, etichette, intestazioni, indirizzi, numeri di telefono, siti, slogan o parole di alcun genere che non siano nell'elenco.
⛔ SE UNA RIGA NON CI STA NELLO SPAZIO, RIDUCI IL CORPO DEI CARATTERI O MANDA A CAPO: non accorciare, non riassumere e non riscrivere le parole. Una riga piu' piccola e' corretta, una riga storpiata rende il manifesto inutilizzabile.
I nomi propri sono la cosa che si sbaglia di piu': {compitato}. Rileggili sul manifesto finito e confrontali lettera per lettera con questa riga.

Colori: {com['colori']}. Il contrasto fra testo e fondo deve essere alto: in strada i toni delicati spariscono.
Prima di consegnare rileggi tutto il testo lettera per lettera, confrontandolo con l'elenco qui sopra: ogni riga deve essere identica, senza parole ripetute, storpiate o inventate. ⛔ Attenzione ai nomi di luogo: si scrivono soltanto "Bagnoli" e "Fuorigrotta", e non devono comparire altre parole che gli somigliano. Accenti e apostrofi corretti, nessuna riga tagliata o coperta dalla figura.
Escludi: titoli ed etichette non richiesti, fasce che dividono la tela in due, figura intera, ripresa di profilo, foto di gruppo, paesaggio nitido, aspetto da cartone animato, resa CGI, pelle di plastica, levigatura eccessiva del viso, bandiere, simboli di partiti diversi da quello allegato, firme, filigrane."""


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--candidato", help="chiave del candidato (es. rosa)")
    p.add_argument("--elenco", action="store_true", help="elenca i candidati salvati")
    p.add_argument("--dati", default=DATI, help=f"file delle impostazioni (default: {DATI})")
    p.add_argument("--senza-simbolo", action="store_true", dest="senza_simbolo",
                   help="l'angolo del simbolo resta VUOTO: il logo vero lo incolla "
                        "poi _tools/sostituisci_simbolo.py (consigliato)")
    p.add_argument("--uscita", help="scrive il prompt su file invece che a schermo")
    a = p.parse_args()

    percorso = os.path.expanduser(a.dati)
    if not os.path.exists(percorso):
        sys.exit(f"⛔ impostazioni non trovate: {percorso}")
    d = json.load(open(percorso, encoding="utf-8"))
    cand, com = d["candidati"], d["_comuni"]

    if a.elenco or not a.candidato:
        print(f"Candidati salvati in {a.dati}:\n")
        for k, c in cand.items():
            print(f"  {k:<12} {c['nome']} {c['cognome']:<12} {c['ruolo']:<12} "
                  f"→ {'barra il simbolo' if c['ruolo'] == 'presidente' else 'scrivi il cognome'}")
            if c.get("note"):
                print(f"               {c['nome'].title()}: {c['note']}")
        if not a.candidato:
            print("\nUsare --candidato <chiave> per generare il prompt.")
        return

    k = a.candidato.lower()
    if k not in cand:
        sys.exit(f"⛔ '{k}' non c'e'. Disponibili: {', '.join(cand)}")
    c = cand[k]
    testo = prompt(c, com, a.senza_simbolo)

    if a.uscita:
        open(os.path.expanduser(a.uscita), "w", encoding="utf-8").write(testo + "\n")
        print(f"scritto: {a.uscita}")
    else:
        print(testo)

    print(f"\n─── allegati, da {c['cartella_foto']}/ ───", file=sys.stderr)
    if a.senza_simbolo:
        print("  A1, A2, A3, A4 (le quattro foto) · c (schema muto) — NIENTE logo",
              file=sys.stderr)
        print("  poi: _tools/sostituisci_simbolo.py per incollare il simbolo vero",
              file=sys.stderr)
    else:
        print("  A1, A2, A3, A4 (le quattro foto) · B (logo) · c (schema muto)",
              file=sys.stderr)
    if c.get("note"):
        print(f"⚠️  {c['note']}", file=sys.stderr)


if __name__ == "__main__":
    main()
