# Regole operative — Partecipazione Attiva

## PRIMA DI TOCCARE IL SITO: leggere il manuale

Il manuale completo di gestione del sito sta **fuori da questo repository**
(qui dentro no: il repository e' pubblico e il manuale contiene la mappa del
computer):

    ~/Desktop/LAVORI/_MANUALI_CLAUDE/MANUALE_SITO_PA_UNIVERSALE.md

Dentro c'e' tutto: architettura, mappa del Mac e del repository, come si
pubblica un articolo, ricerca, assistente, mappa iscritti, accessibilita',
privacy, la tabella di **tutti** gli strumenti gia' pronti in `_tools/`, la
checklist prima del push e il registro delle trappole gia' pagate.

Vale per chiunque legga questo file: Claude, un'altra IA o una persona.
**Prima di scrivere uno script nuovo, guardare se esiste gia'** (manuale §17).

## Decidere, non domandare — vale SEMPRE

Fernando non ha competenze tecniche: una domanda tecnica non gli dà modo di
rispondere, gli sposta addosso una decisione che è mia. Il calcolo costi/benefici
lo faccio io.

- **Le scelte tecniche le decido ed eseguo io**: commit, push, quale approccio,
  se fare una pulizia, come strutturare uno script. Mai "lo sistemo?", mai
  "vuoi che committi?". Finito il lavoro: committo, pusho, e riferisco cosa ho
  fatto e cosa ho **verificato** (con la prova, non con un'impressione).
- **Si chiede solo su risvolti legali o privacy**: dati personali degli iscritti,
  pubblicazione di nomi, contenuti che espongono il movimento.
- Se una modifica è rischiosa, la rendo **reversibile** (branch, backup) invece di
  chiedere il permesso.
- Le verifiche le faccio io: mai "controlla tu se funziona".

### Tutto quello che posso fare io, lo faccio io (28 luglio 2026)

Detto da Fernando: *«tutto quello che puoi fare tu fallo, io intervengo solo se
non c'è altro modo»*. Non è un permesso occasionale, è la regola di ingaggio.

**Non gli si passa il lavoro.** Niente "preferisci scriverlo tu?", niente
"dimmi se lo aggiungo io", niente elenchi di cose da fare che potrei fare io.
Se la sto scrivendo come domanda ma so già come si fa, allora la faccio.

Restano a Fernando **solo** le cose che tecnicamente non posso fare al posto suo:

- creare account, inserire password o credenziali;
- pubblicare a nome del movimento su piattaforme esterne (Wikidata, social,
  moduli, iscrizioni);
- azioni dentro servizi che richiedono il suo accesso (Search Console:
  «Richiedi indicizzazione», e simili);
- risvolti legali o privacy, e i contenuti che espongono il movimento (unica
  categoria in cui la domanda è dovuta, come sopra).

Quando una di queste ricorre: **preparo tutto** — testo pronto da incollare,
passaggi in ordine, dati verificati — e gli lascio solo il gesto finale. Mai
la ricerca, mai la decisione, mai la stesura.

Contenuto politico e fattuale (numeri di una legge, cronaca dell'iter) **lo
scrivo io** con le fonti in mano: non rientra nell'eccezione, che riguarda ciò
che espone il movimento, non ciò che lo informa.

## Punti fissi — identità operative del movimento

Valori da usare **sempre**, senza chiedere. Elenco da ampliare quando se ne
fissano altri.

- **Iscrizioni a servizi e verifiche via posta elettronica:**
  `webmaster.partecipazione.attiva@gmail.com`
  Vale per qualunque registrazione fatta per conto del movimento (Wikidata,
  strumenti, piattaforme, verifiche). **Non** l'indirizzo personale di Fernando,
  e **non** `partecipazioneattiva21@gmail.com`, che è l'indirizzo pubblico di
  contatto mostrato sul sito e serve ad altro.
  Fissato il 28 luglio 2026.

## Consumo crediti (piano **Max 5x**, 90 €/mese) — vale SEMPRE, senza che l'utente lo chieda

Il contesto viene rispedito e ripagato a ogni messaggio: il costo di una sessione
cresce col **quadrato** della sua lunghezza. 50 messaggi non costano 50, costano ~1.250.

Da applicare di default, non su richiesta:

1. **Proporre `/clear` quando cambia il lavoro.** Finito il TG → `/clear` prima del
   sito. Finito il sito → `/clear` prima dei social. Dirlo io, non aspettare.
2. **Piano prima, esecuzione dopo** su qualsiasi lavoro non banale. Rifare costa
   sempre più che pianificare. Prima di scrivere descrizioni/testi su una pagina,
   **leggere la pagina di destinazione**.
3. **Niente giri a vuoto.** Se lo stesso difetto compare due volte, è una causa a
   monte: fermarsi e trovarla. Ogni tentativo fallito resta nel contesto e si
   ripaga fino a fine sessione.
4. **Modifiche ripetitive su molte pagine → script in `_tools/`**, mai a mano.
   Uno script che tocca 56 pagine costa quanto una richiesta.
5. **Filtrare l'output verboso** prima di leggerlo (`| grep -i error | head -20`),
   non versare log interi nel contesto.
6. **Lavori pesanti in sequenza**, mai in parallelo.
7. **Le scoperte vanno negli script e nei manuali** (`~/Desktop/LAVORI/_MANUALI_CLAUDE`),
   non riderivate in conversazione.

Manuale completo: `~/Desktop/LAVORI/_MANUALI_CLAUDE/MANUALE_CREDITI_CLAUDE_v1.md`

### Quale modello — abbiamo anche Fable 5 (29 luglio 2026)

| Modello | Quando |
|---|---|
| **Fable 5** | il problema difficile lasciato girare **da solo, di notte**. ⚠️ **pesca dallo stesso serbatoio settimanale** degli altri modelli (la barra "Fable" è un tetto al 50%, non un'aggiunta) ed è il modello più caro: consuma più in fretta. In più i suoi turni durano molti minuti — **non** per il lavoro interattivo dove Fernando corregge in corsa |
| **Opus 5** | il quotidiano che richiede giudizio: TG, debug, decisioni che poi si pagano |
| **Sonnet 5** | ripetitivo ma non stupido: menu, script, card |
| **Haiku 4.5** | meccanico e verificabile: rinominare, riordinare, formattare |

Si cambia con `/model` e **la conversazione resta**: il modello nuovo vede tutto
lo scambio. Ma il cambio **azzera la cache**, quindi si cambia quando cambia il
lavoro, non avanti e indietro dentro lo stesso.

⚠️ La continuita' vera non e' la conversazione, sono i **file**: manuali,
`lessico/`, `archivio_notizie/`, script e memoria stanno su disco e li legge
qualunque modello, anche dopo un `/clear`. Dettagli nel manuale crediti §3.1-3.2.

## Sito

- HTML statico su GitHub Pages, **nessun template condiviso**: ogni pagina si porta
  dentro la propria copia del menu. Per cambiare il menu: `_tools/allinea_menu.py`.
- Rotazione card home → archivio: `_tools/ruota_home.py` (`--applica` per scrivere).
- Alcune voci di menu puntano a **sezioni della home**, non a pagine: contare i link
  entranti prima di rimuovere una sezione.
