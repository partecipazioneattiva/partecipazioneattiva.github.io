# Rapporto tecnico sul sito — 26 luglio 2026

Analisi misurata su **65 pagine**. Strumenti ripetibili:
`_tools/analizza_sito.py` (struttura, accessibilità, link, SEO, immagini) e
misure di resa reale nel browser su `partecipazione-attiva.it` e sul server
locale. Ogni voce qui sotto è un numero, non un'impressione: si può rimisurare
dopo ogni intervento.

> Cartella `_audit/`: come tutte le cartelle con l'underscore, **non viene
> pubblicata** da GitHub Pages. Questo rapporto resta interno.

---

## 1. GRAVE — Il sito traccia i visitatori, e l'informativa dice di no

**Fatto misurato.** Aprendo la home, il browser del visitatore contatta
**9 domini di terze parti** prima che lui abbia fatto qualsiasi cosa:

| servizio | cosa fa | su quante pagine |
|---|---|---|
| `googletagmanager.com` | Google Tag Manager (statistiche) | 51 |
| `clarity.ms` (+ `n.`, `scripts.`) | **Microsoft Clarity: registra la sessione** — clic, scorrimento, movimenti del mouse, e li riproduce come un video | 51 |
| `webpushr.com` (+ `bot.`, `analytics.`) | notifiche push, assegna un identificativo al dispositivo | 51 |
| `fonts.googleapis.com` | caratteri tipografici serviti da Google (trasmette l'IP del visitatore) | 63 |
| `api.rss2json.com` | ponte esterno per il feed RSS | 2 |

**Cosa dice invece l'informativa** (`privacy.html`, §8, testo visibile):

> «Il presente sito, essendo un sito statico ospitato su GitHub Pages, non
> utilizza cookie propri per il tracciamento o la profilazione degli utenti.
> Potrebbero essere presenti cookie tecnici di terze parti relativi a:
> GitHub Pages … Google Fonts …»

Clarity, Google Tag Manager e Webpushr **non sono nominati da nessuna parte**
nel testo dell'informativa (verificato togliendo gli script e cercando nel solo
testo leggibile: 0 occorrenze di "Clarity", 0 di "analytics", 0 di "Webpushr").

**Non esiste alcun banner di consenso** su nessuna delle 65 pagine (0 occorrenze
di "consenso" nel testo dell'informativa; nessun banner cookie nel codice).
Quindi il tracciamento parte **prima** che il visitatore possa scegliere.

**Perché è grave, in concreto:**

1. Microsoft Clarity non è una statistica anonima: è una **registrazione della
   sessione**. Chi ha accesso al pannello può guardare cosa ha fatto un
   visitatore sul sito, riquadro per riquadro.
2. Sulle pagine del movimento passano persone che aderiscono a battaglie
   politiche. Registrarne il comportamento e mandarlo a Microsoft e Google è
   diverso dal contare le visite.
3. C'è una contraddizione interna che pesa: l'assistente PensAttivo è stato
   costruito apposta perché **nessun dato uscisse dal browser**, e nella stessa
   pagina ci sono tre servizi di terzi che raccolgono.
4. Un'informativa che descrive una situazione diversa da quella reale è il
   problema più serio dei tre: non è una svista tecnica, è un documento
   pubblicato che non corrisponde ai fatti.

**Questo NON lo decido io.** Non sono un legale e la scelta è del direttivo.
Le vie possibili, in ordine di semplicità:

- **A — Togliere il tracciamento** (Clarity, Tag Manager, Webpushr): il sito
  torna coerente con la sua informativa, non serve nessun banner, e le
  statistiche si perdono. Tecnicamente è mezz'ora di lavoro su 51 pagine.
- **B — Tenerlo e mettersi in regola**: banner di consenso preventivo che
  blocca gli script finché il visitatore non accetta, più informativa riscritta
  con l'elenco vero dei servizi. È più lavoro e appesantisce il sito.
- **C — Via di mezzo**: togliere la registrazione di sessione (Clarity, la più
  invasiva), tenere le sole statistiche aggregate e le notifiche, e allineare
  l'informativa.

In ogni caso, una cosa va fatta comunque: **ospitare i caratteri tipografici
sul sito** invece di prenderli da `fonts.googleapis.com`. Oggi ogni visitatore,
su 63 pagine, comunica il proprio indirizzo IP a Google solo per vedere il
testo scritto giusto. Costa pochi minuti e non toglie niente a nessuno.

---

## 2. La duplicazione: 430 KB di stile identico, riscaricati a ogni pagina

| misura | valore |
|---|---|
| HTML totale | 1.874 KB su 65 pagine (media 29 KB) |
| di cui CSS scritto dentro le pagine | 624 KB (33%) |
| di cui JS scritto dentro le pagine | 265 KB (14%) |
| **CSS identico ripetuto pagina per pagina** | **430 KB** |

Non è solo peso: è la ragione per cui **un difetto va corretto 65 volte**.
I problemi di contrasto del punto 3 stanno tutti nell'intestazione ripetuta:
un unico foglio di stile li chiuderebbe in un posto solo.

Effetto pratico di un foglio unico: il visitatore lo scarica **una volta**, e
dalla seconda pagina in poi ogni pagina pesa circa 10 KB invece di 29.

**Menu disallineato** — la conseguenza già visibile della stessa causa:

- **8 versioni diverse** del menu sulle 55 pagine che ce l'hanno;
- **10 pagine senza `<nav>`** (`404.html`, `azioni.html`, `cancella.html` e altre 7);
- le divergenze non sono casuali: a 12 pagine manca la voce del modulo
  d'iscrizione Google, a `sanitapubblica.html` e alle due pagine
  `pensattivo-rapporti` mancano più di dieci voci.

---

## 3. Accessibilità — il punto dove il pubblico di PA perde di più

Misurato con il browser a 375 px (telefono), calcolando il contrasto reale
come lo calcolano le linee guida WCAG.

| misura | home | articolo tipo (`stabilicum.html`) |
|---|---|---|
| **testo di lettura** | — | **14,1 px** (lo standard comodo è 16-17) |
| testi sotto i 14 px | 153 | 61 |
| contrasto sotto la soglia, **certi** | 23 | 15 |
| contrasto da verificare a occhio (testo su immagine) | 71 | 7 |
| bersagli da toccare più piccoli di 24 px | 27 | 10 |
| sbordamento orizzontale | no | no |

Esempi certi, gli stessi su tutte le pagine perché stanno nell'intestazione:
«Sostienici» **2,5:1** (serve 4,5), «Iscriviti» **4,2:1**, i badge delle card
a 9-11 px con **2,5:1**.

**Cosa va bene:** tutte le **245 immagini hanno il testo alternativo** — non
una mancante, non una vuota. È un risultato raro e va detto. Nessun id
duplicato, nessun link dal testo vago tipo "clicca qui", nessuno sbordamento
laterale su telefono.

**Cosa non va, oltre a contrasto e dimensioni:** 8 pagine saltano un livello di
titolo (da h1 a h3), 3 pagine hanno più di un h1, e le due pagine di verifica
Google non hanno né `lang` né titolo (irrilevanti per chi legge, ma restano
pagine pubbliche).

---

## 4. Peso e velocità

Misurato sul sito vero, che comprime:

- home: **17 KB di HTML scaricati** (72 KB decompressi) — la compressione
  funziona bene;
- **totale della pagina: 2.040 KB**, di cui **1.603 KB di immagini**;
- primo disegno a **888 ms**, pagina pronta a **603 ms**: veloce;
- 37 risorse richieste, 9 domini di terzi (punto 1).

Immagini, sull'intero sito: **82 file per 9,6 MB**, quasi tutte già in formato
moderno (48 `.webp`, 1 `.jpg`, 1 `.png`: la conversione è stata fatta bene).
Quattro superano i 300 KB (`ape-copertina.webp` 636 KB).

Il difetto vero è un altro: **solo 21 immagini su 245 dichiarano larghezza e
altezza**, e 153 su 245 hanno il caricamento differito. Senza le dimensioni
dichiarate la pagina **salta mentre carica** — il lettore anziano perde la riga
e ricomincia da capo. È fastidio puro, e si corregge con uno script.

---

## 5. Collegamenti e metadati

- **4 link interni rotti**, tutti in `mappa.html`: sono indirizzi scritti senza
  `https://`, quindi il browser li cerca dentro il sito e trova il nulla. Uno è
  testo finito per sbaglio dentro un collegamento
  (`www.auragruppoconsumatori.it.    www.omniaworld.it www.partecipazione-attiva.it`).
- Ancore interne: **0 rotte**. Sitemap: **46 voci, mancano 14 pagine**
  pubbliche (`archivio.html`, `azioni.html` e altre 12).
- **17 pagine senza `canonical`**, 9 senza immagine per l'anteprima social,
  8 senza descrizione.
- **25 titoli oltre i 65 caratteri** (Google li taglia) e 18 descrizioni oltre
  i 160.

---

## 6. Ordine del cantiere

Fuori dal sito ma dentro il lavoro: nella cartella principale del repository
ci sono script di correzione una-tantum mai archiviati (`fix_stabilicum.py`,
`fix_stabilicum_wrap.py`, `fix_spanu_qualifica.py`), appunti (`spanu-congresso-bp.txt`)
e video non versionati. Non si vede dal sito, ma è disordine che prima o poi
costa: gli strumenti stanno in `_tools/`, il resto va archiviato o buttato.

---

## VERDETTO

**Sì, i presupposti per una ristrutturazione ci sono — ma mirata, non un sito
nuovo.** Rifare il sito da capo butterebbe via cose che funzionano e che sono
costate lavoro: la ricerca, PensAttivo, il motore di pubblicazione con i suoi
controlli, i testi alternativi su 245 immagini. Il difetto non è il progetto:
è che **ogni pagina si porta dentro la propria copia di tutto**, e quindi ogni
difetto è copiato 65 volte.

Ordine consigliato, dal più urgente:

| # | intervento | perché | dimensione |
|---|---|---|---|
| 1 | **Decidere sul tracciamento** e allineare l'informativa | è la sola voce legale: il documento pubblicato non corrisponde ai fatti | decisione del direttivo, poi mezza sessione |
| 2 | Caratteri tipografici ospitati sul sito | toglie l'IP dei visitatori a Google, non ha controindicazioni | mezz'ora |
| 3 | **Un foglio di stile unico** al posto delle 65 copie | -430 KB duplicati, e da lì in poi ogni difetto si corregge in un posto solo | una sessione, reversibile |
| 4 | Accessibilità: testo a 16-17 px, contrasti a norma | è il pubblico di PA: pensionati, spesso su telefono | mezza sessione (dopo il 3, si fa in un file) |
| 5 | Menu riallineato su tutte le pagine + controllo automatico | 8 versioni diverse in giro | mezza sessione |
| 6 | Immagini: larghezza/altezza dichiarate, le 4 pesanti alleggerite | la pagina smette di saltare mentre carica | mezza sessione, tutto a script |
| 7 | Sitemap, canonical, titoli lunghi, 4 link rotti | igiene, si fa a script | mezza sessione |
| 8 | Ordine nel repository | debito che cresce | poco |

I punti 3 e 4 sono lo stesso cantiere e vanno fatti insieme. Il punto 1 non è
tecnico e aspetta una decisione.
