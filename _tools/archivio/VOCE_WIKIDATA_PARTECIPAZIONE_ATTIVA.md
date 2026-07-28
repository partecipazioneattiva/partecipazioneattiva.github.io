# Voce Wikidata — Partecipazione Attiva

Preparata il 28 luglio 2026. **Da pubblicare a mano da Fernando**: creare account e
pubblicare contenuti a nome del movimento non lo faccio io.

Serve a dire a Google, e alle intelligenze artificiali che rispondono al posto suo,
che «partecipazione attiva» non è soltanto una locuzione italiana: è anche un
movimento preciso, con un portavoce, una sede, un sito. È la leva più forte che
avete, perché il nome del movimento è una frase comune e oggi Google non sa
distinguere le due cose.

---

## 1. Prima di iniziare: si può fare?

Wikidata accetta una voce se «si riferisce a un'entità chiaramente identificabile,
descrivibile con **fonti serie e pubblicamente disponibili**». Non bastano il vostro
sito e i vostri social: servono fonti **di terzi**. Ne avete due, verificate:

| fonte | data | cosa dice |
|---|---|---|
| **Radio Radicale**, scheda 793958 | 10 luglio 2026 | archivia il convegno di Roma sulla legge elettorale: «Luigi Spanu, portavoce di Partecipazione Attiva», moderatore, con Gherardo Colombo, Riccardo Magi, Dario Parrini, Carmela Auriemma, Christian Ferrari (CGIL) |
| **Articolo21**, firma Roberto Zaccaria | 15 luglio 2026 | elenca «Partecipazione attiva (Spanu)» fra le organizzazioni della *Rete per un voto libero e uguale* |

Sono sufficienti. Radio Radicale è archivio di riferimento della politica italiana,
Articolo21 è testata registrata. **Se in futuro arrivano altre citazioni sulla
stampa, aggiungerle**: più fonti indipendenti, più la voce è al sicuro.

**Onestà**: dichiarare che si sta scrivendo del proprio movimento. Nella descrizione
della modifica scrivere per esempio *«creo la voce del movimento di cui faccio
parte, con fonti di stampa indipendenti»*. Wikidata non lo vieta, ma nasconderlo
è il modo più rapido per farsi cancellare la voce.

---

## 2. Come si pubblica

1. Andare su **wikidata.org** e creare un account (serve solo un nome utente e una
   password; l'email è facoltativa ma conviene, per recuperare l'accesso).
2. Menu a sinistra → **«Crea un nuovo elemento»**.
3. Compilare **etichetta**, **descrizione** e **alias** copiando dal punto 3 qui
   sotto.
4. Salvare. Comparirà un codice tipo **Q123456789**: è l'identificativo della voce.
   **Segnarlo e passarmelo**, serve per il punto 6.
5. Aggiungere una per una le dichiarazioni del punto 4, ognuna con la sua fonte.

---

## 3. Etichetta, descrizione, alias

**Etichetta (italiano):**
```
Partecipazione Attiva
```

**Descrizione (italiano)** — è la riga che scioglie l'ambiguità col significato
comune delle parole, la parte più importante di tutta la voce:
```
movimento civico italiano fondato nel 2021
```

**Etichetta (inglese):**
```
Partecipazione Attiva
```

**Descrizione (inglese):**
```
Italian civic political movement founded in 2021
```

**Alias (italiano)** — uno per riga:
```
PA
Movimento Popolare dei Cittadini Italiani
Partecipazione Attiva - Movimento Popolare dei Cittadini Italiani
```

---

## 4. Le dichiarazioni

Ognuna si aggiunge con «+ aggiungi dichiarazione». Per la fonte: sotto la
dichiarazione, «+ aggiungi riferimento» → proprietà **URL di riferimento (P854)** →
incollare il link → e **consultato il (P813)** → 28 luglio 2026.

I nomi qui sotto sono **esattamente** quelli che compaiono nell'interfaccia in
italiano: scrivendoli nella casella, la proprietà giusta appare nel menu a tendina.
Il codice fra parentesi è la conferma che si è scelta quella corretta.

| proprietà (come si chiama a schermo) | valore | fonte da mettere |
|---|---|---|
| **istanza di** (P31) | `movimento politico` (Q2738074) | Articolo21 |
| **istanza di** (P31) | `associazione` (Q48204) | il vostro statuto |
| **paese** (P17) | `Italia` (Q38) | — |
| **data di fondazione o creazione** (P571) | `2021` (basta l'anno) | pagina Chi siamo |
| **sito web ufficiale** (P856) | `https://partecipazione-attiva.it/` | — |
| **sede legale** (P159) | `Napoli` (Q2634) | pagina Napoli |
| **identificativo Facebook** (P2013) | `PartecipazioneAttiva21` | — |
| **identificativo YouTube di un canale** (P2397) | ricavarlo dal canale (vedi nota) | — |
| **nome utente TikTok** (P7085) | `partecipazione.at` | — |

**Nota sull'identificativo YouTube**: P2397 vuole il codice che comincia per `UC`,
non `@partecipazioneattiva`. Si trova aprendo il canale → tre puntini → Condividi
canale → Copia ID canale. Se non lo si trova, **saltare questa riga**: meglio
nessun dato che un dato sbagliato.

**Da NON mettere adesso:**
- *partito politico*: non lo siete ancora. Il giorno che presentate una lista o vi
  registrate come partito, si aggiunge allora — la voce resta la stessa e si
  aggiorna con una riga.
- persone (presidente, portavoce): richiedono una voce propria a testa, e ognuna
  deve reggere da sola il requisito delle fonti. Si fa in un secondo momento, se
  le citazioni sulla stampa aumentano.

---

## 5. Se qualcuno propone la cancellazione

Può succedere, ed è normale: non è un'accusa. Si risponde nella pagina di
discussione indicando le due fonti del punto 1 per esteso — testata, data, cosa
dicono. Una voce con fonti di terzi verificabili di solito resta.

---

## 6. Dopo la pubblicazione — questo lo faccio io

Passami il codice `Q...` e chiudo il cerchio:

1. Aggiungo il link Wikidata al `sameAs` dei dati strutturati del sito. Serve a
   collegare le due identità nei due sensi: gli esperti misurano che i marchi con
   **4 o più profili verificati** ottengono il pannello informativo di Google
   **4,1 volte più spesso**. Oggi ne avete 3 (Facebook, YouTube, TikTok):
   **Wikidata è il quarto**.
2. Aggiorno `llms.txt`, la scheda che il sito offre alle intelligenze artificiali.
3. Segnalo il cambiamento a Bing e Copilot con `python3 indexnow.py index.html`.

---

## Stato dei dati del sito al 28 luglio 2026

Già sistemato: i dati strutturati della home dichiaravano **`PoliticalParty`**
(partito politico) mentre la pagina Chi siamo dice «non siamo un partito: siamo un
movimento civico». Corretto in `Organization`, con descrizione allineata.
