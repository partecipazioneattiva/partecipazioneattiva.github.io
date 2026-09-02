# Regole operative — Partecipazione Attiva

## SI COMINCIA DA QUI — due comandi, non trentaquattro file

    ~/Desktop/ARCHIVIO GENERALE/LAVORI/_MANUALI_CLAUDE/INDICE.md

**L'indice dice quale manuale apre cosa.** Si legge quello, si apre **solo** il
manuale che serve, non tutti: la documentazione e' 1,1 MB e leggerla intera
costa una sessione. (Fuori dal repository: e' pubblico e i manuali contengono
la mappa del computer.)

Se qualcosa sembra rotto, o prima di un lavoro lungo:

```bash
zsh ~/Desktop/SCRIPT/sistema/verifica_tutto.sh
```

In venti secondi dice se reggono l'interprete del TG, gli strumenti, i percorsi
che tutto da' per scontati, i collegamenti, il repository e gli scarichi.
**Prima si guarda questo, poi si diagnostica** — non il contrario.

## LA GUARDIA — otto regole che non dipendono più dalla memoria

Sono errori **fermati dal computer**, non affidati alla buona volonta' di chi
lavora (hook `PreToolUse`, script in
`~/Desktop/SCRIPT/sistema/guardia_comandi.sh`).

Le tre trappole di casa (dal 5 agosto 2026):

1. **`git add -A`** nel repository — e' pubblico. Si aggiunge **per nome**.
2. **`python3` nudo** sugli script del TG che caricano il modello
   (02 03 05 06 08 11 15 17 18 20 21 22 23 24). Il 07 e il 13 passano.
3. **Gli allineamenti audio sospesi** (10, 16, 19, `--allinea`): l'audio del
   TG **si consegna grezzo**.

I cinque divieti permanenti (dal 16 agosto 2026, quando la **modalita'
automatica** e' diventata il default di Claude Code):

4. **`sudo`** — chiede la password di Fernando: quella non la digita l'IA.
5. **Push forzato o riscrittura della storia** (`--force`, `-f`, `--mirror`,
   `--delete`, `filter-branch`): il repository e' pubblico, un errore si ripara
   **in avanti**, con un commit nuovo che si vede.
6. **Cancellazioni fuori dal perimetro**: `/`, la cartella personale, i quattro
   pilastri della Scrivania, e le formattazioni di disco.
7. **Lettura dei file di credenziali** (chiavi SSH, token, portachiavi): quello
   che non entra nella conversazione non puo' finire per sbaglio in un commit.
8. **`curl ... | sh`** — codice scaricato ed eseguito senza averlo letto.

Chi prova, riceve il motivo e cosa fare invece. Non e' un promemoria: e' un
blocco. La guardia sta **fuori dal repository** perche' nomina i percorsi del
computer, ed e' registrata in `~/.claude/settings.json`, che non finisce su
GitHub — a livello di **utente**, cosi' vale in ogni cartella del Mac e non
solo qui. Accanto, in `permissions.deny`, ci sono le stesse regole in forma di
permesso: coprono anche la **lettura** dei file di credenziali, che non passa
da un comando e quindi l'hook non la vedrebbe.

🟨 In caso di dubbio la guardia **lascia passare**: un blocco sbagliato ferma il
lavoro, un blocco mancato lo rallenta e basta.

⚠️ Una regola nuova che deve valere **sempre** va scritta li', non qui: un
divieto detto in chat, in modalita' automatica, viene riletto dal filo della
conversazione — e la compattazione del contesto puo' cancellarlo. Si scrive come
ricerca sull'**intero** comando, e si prova con una batteria «deve bloccare /
deve passare» prima di considerarla fatta.

## PRIMA DI TOCCARE IL SITO: leggere il manuale

Il manuale completo di gestione del sito sta **fuori da questo repository**
(qui dentro no: il repository e' pubblico e il manuale contiene la mappa del
computer):

    ~/Desktop/ARCHIVIO GENERALE/LAVORI/_MANUALI_CLAUDE/MANUALE_SITO_PA_UNIVERSALE.md

Dentro c'e' tutto: architettura, mappa del Mac e del repository, come si
pubblica un articolo, ricerca, assistente, mappa iscritti, accessibilita',
privacy, la tabella di **tutti** gli strumenti gia' pronti in `_tools/`, la
checklist prima del push e il registro delle trappole gia' pagate.

Vale per chiunque legga questo file: Claude, un'altra IA o una persona.
**Prima di scrivere uno script nuovo, guardare se esiste gia'** (manuale §17).

## PRIMA DI FARE IL TG: leggere la procedura blindata

Anche il TG passa da questo repository (le card e il ticker), ma **si produce
altrove**, e la sua procedura e' **imperativa**:

    ~/Desktop/SCRIPT/tg/PROCEDURA_BLINDATA.md

Si esegue **così ogni volta, senza la minima modifica** (ordine di Fernando,
01/08/2026). Accanto, `MANUALE_PIPELINE_TG.md` spiega il **perche'**: misure,
prove fallite, registro delle modifiche. Entrambi sono raggiungibili anche da
`_MANUALI_CLAUDE/` (sono collegamenti, non copie: **mai sostituirli con copie**).

Le tre cose che si sbagliano piu' spesso, se non si legge:
`python3` nudo non funziona (serve l'interprete dell'ambiente conda), **l'audio
si consegna grezzo** (niente `--allinea`, `16`, `19`), e il **`reference_text`
del copione si copia dal `.txt` accanto all'audio**, mai a memoria.

⚠️ Quando si pubblica un TG, sul sito i posti da aggiornare sono **tre**:
card in `webtv.html`, card nella home, voce del ticker.

## ⛔ Le cartelle nuove nascono in `Claude IA`, non sulla Scrivania (13 agosto 2026)

Ordine di Fernando: *«se in futuro devi fare nuove cartelle per i nostri lavori
vanno automaticamente dentro Claude, non ad intasare la scrivania»*.

**Quando serve una cartella per un lavoro nuovo** — un manifesto, un dossier,
una prova di voce, una campagna — si crea **dentro il reparto giusto** di:

    ~/Desktop/ARCHIVIO GENERALE/Claude IA/

    01_TG_E_STAMPA         notiziario, podcast Parlero', materiali per la stampa
    02_VOCI_E_MUSICA       voci, basi, prove microfono
    03_VIDEO_E_DIRETTE     dirette Zoom/OBS, clip verticali
    04_MANIFESTI_E_CARD    le immagini che escono col nome del movimento
    05_ELEZIONI_E_DOSSIER  candidature, leggi, dossier

Si sceglie il reparto **per scopo**, cioe' per cosa si sta cercando di fare. Se
nessuno dei cinque calza si aggiunge un reparto nella tabella dentro
`~/Desktop/SCRIPT/sistema/stanza_claude.py`, e si aggiorna `Claude IA/MAPPA.md`
rilanciandolo — non si apre un'eccezione sulla Scrivania.

## ⛔ Le cartelle della Scrivania le AUTORIZZA Fernando (27 agosto 2026)

Ordine di Fernando, che **cambia la regola** del 26 agosto: *«cambia la regola,
prime pagine resta e le cartelle in scrivania possono aumentare se autorizzate
da me»*.

**Non sono piu' due cartelle sole.** La Scrivania ha un elenco di cartelle
autorizzate, e l'autorizzazione la da' **lui**.

⛔ **Una cartella o un collegamento che non conosco NON e' un difetto**: e' una
cosa che puo' aver autorizzato senza dirmelo. Si **segnala e si chiede**, non si
propone di toglierlo e non si conta come violazione.
⛔ **Io non ne creo e non ne tolgo**: le cartelle della Scrivania le decide lui.

Autorizzate a oggi:

    ~/Desktop/SCRIPT/                 gli strumenti
    ~/Desktop/ARCHIVIO GENERALE/      tutto il resto del lavoro
    ~/Desktop/PRIME PAGINE/           autorizzata il 27/08/2026 — resta
    ~/Desktop/LAVORI ->               collegamento ad ARCHIVIO GENERALE/LAVORI,
                                      rimesso il 30/08/2026: *«messo per
                                      recuperare concatenazioni, lascialo
                                      stare»*. Serve a far ritrovare a Claude le
                                      conversazioni che si portano dentro il
                                      vecchio indirizzo. NON si tocca.

🟥 **Trappola pagata il 02/09/2026**: questa sezione diceva ancora «DUE
cartelle», perche' la regola nuova del 27/08 era finita **solo in memoria**.
Fidandomi di qui ho segnalato `LAVORI` come anomalia e ho proposto di toglierlo
— esattamente cio' che la regola vieta. 👉 **Una regola che cambia si riscrive
QUI, non solo in memoria**: questo file e' quello che si legge a ogni avvio.

Il riordino del 26 agosto resta valido per tutto il resto:

    ~/Desktop/SCRIPT/                 gli strumenti — resta fuori, si usa ogni giorno
    ~/Desktop/ARCHIVIO GENERALE/      tutto il resto

Dentro `ARCHIVIO GENERALE`, ai vecchi nomi:

    LAVORI/               sito, manuali, lavorazioni del TG
    Claude IA/            i lavori nuovi, nei cinque reparti
    AI_TOOLS/             Applio, LivePortrait, RVC, chatterbox…
    PENSATTIVO IMMAGINI/
    _ARCHIVIO/            il chiuso, con la via del ritorno
    SCARICATI/            quello che stava in ~/Downloads (`!`, VIDEO_YOUTUBE, BACKUP_KODI)
    MANUALI CLAUDE ->     collegamento a LAVORI/_MANUALI_CLAUDE

⛔ `~/Downloads` si lascia **vuota**: quello che ci arriva si sposta in
`ARCHIVIO GENERALE/SCARICATI`. La cartella del TG **non e' piu'**
`~/Downloads/TG`: e' `~/Desktop/ARCHIVIO GENERALE/SCARICATI/!/TG`.

✋ **`~/Desktop/PRIME PAGINE` non si sposta.** Non e'
roba accumulata: e' il piano di lavoro di `SCRIPT/prime_pagine.py`, che **la
svuota a ogni lancio** e ci rifa' dentro le prime pagine dai PDF appena
scaricati in `~/Downloads` — che infatti si riempie e si svuota tutti i giorni,
ed e' proprio per questo che lo script guarda li'. La nominano
`prime_pagine.py`, `scarica_rassegna_completa_v16.py` e `SCRIPT/LEGGIMI.md`:
spostarla vuol dire riscrivere tre script per rendere piu' scomoda la cosa che
si guarda ogni mattina. Chi riordina la Scrivania la **salta**.

🗺️ Dov'era ogni cosa prima: `ARCHIVIO GENERALE/MAPPA_SPOSTAMENTI.md`.

⚠️ Spostare una cartella gia' esistente non e' un `mv`: e' nominata dentro
script, manuali e memoria, e vanno riscritti tutti. Lo fa `stanza_claude.py`.
Dopo qualunque spostamento si rilancia `verifica_tutto.sh`, che trova i
collegamenti rimasti rotti.

## Dove stanno gli script (dal 5 agosto 2026)

Tutti in **`~/Desktop/SCRIPT/`**, con la mappa in `SCRIPT/LEGGIMI.md`:

    SCRIPT/tg/        il TG PensAttivo (era LAVORI/_SCRIPT_TG_PENSATTIVO)
    SCRIPT/sistema/   manutenzione del Mac (era LAVORI/_SCRIPT_SISTEMA)
    SCRIPT/sito ->    collegamento a _tools/ di questo repository
    SCRIPT/*.py       rassegna stampa, video, audio

Unica eccezione, e non e' negoziabile: **gli strumenti del sito restano in
`_tools/` dentro il repository**, perche' sono versionati con git e pubblicati
insieme al sito. Da `SCRIPT/sito` si raggiungono lo stesso.

Nei vecchi posti sono rimasti dei collegamenti perche' niente si rompa, ma
**nei file nuovi si scrive il percorso nuovo**.

## 🥇 REGOLA D'ORO — prima spiego, poi procedo (7 agosto 2026)

Detto da Fernando: *«prima mi spieghi cosa vuoi fare poi procedi, non richiesta
di consenso ma messaggio chiaro per capire io. Poi se dico vai, fai tutto quello
che serve»*.

- Prima di una serie di comandi: **due o tre righe** che dicono **cosa** sto per
  fare e **perché**, in parole sue, non in gergo. «Creo una cartella e ci genero
  dentro l'immagine per il cerchio della webcam», non «eseguo uno script PIL».
- **Non è una richiesta di consenso, e non finisce con una domanda.** Niente
  «procedo?», «va bene?», «vuoi che lo faccia?»: quelle restano vietate dalla
  regola qui sotto. Serve solo a fargli capire cosa succede sul suo Mac.
- Al suo **«vai»**: eseguo **tutto** quello che serve fino in fondo, senza
  fermarmi passo per passo, poi riferisco cosa ho fatto e cosa ho **verificato**.
- Unica eccezione, come sempre: risvolti **legali o di privacy**.
- Se le richieste di permesso dell'app si moltiplicano su comandi innocui,
  **propongo io** di allargare l'elenco dei comandi pre-autorizzati, invece di
  fargliele confermare una per una.

Nata da un caso concreto: durante il lavoro su OBS gli sono arrivate conferme da
approvare per creare una cartella e generare un PNG, senza sapere a cosa
servissero. Un permesso senza contesto è il peggio dei due mondi — lo interrompe
**e** non gli dà gli elementi per decidere.

## 🥇 REGOLA D'ORO — se Fernando scrive, ci si ferma e si legge (17 agosto 2026)

Detto da lui: *«quando senti che scrivo qualcosa qualsiasi cosa stai facendo e sottolineo
qualsiasi ti fermi immediatamente e leggi o per prenderne atto o per rispondere e questo
è tassativo e improrogabile»*.

- Il messaggio arriva a metà turno: **si interrompe la catena di comandi**, si legge, si
  risponde. Non si finisce il file che si stava scrivendo, non si aspetta un punto comodo.
- Vale anche per i messaggi che sembrano commenti: sono spesso correzioni di rotta.
- **Non è una richiesta di consenso**: preso atto, si riprende da soli.
- Se il messaggio cambia i presupposti, si dice **cosa era sbagliato** e si rifà — non si
  consegna lo stesso il pezzo già scritto.

Nata da un caso concreto: mentre scrivevo un calendario per la LIP sulla RC Auto dando per
esistente un testo da emendare, lui aveva già scritto che la LIP non esiste ancora. Minuti
di lavoro buttati, e uno schermo che non lo ascoltava.

## 🥇 REGOLA D'ORO — super partes, mai per compiacere (17 agosto 2026)

Detto da Fernando: *«qualsiasi azione/lavoro non deve essere fatto in modo di compiacermi
ma sempre superpartes e analitico dei fatti»*.

Lui usa quello che gli consegno per decidere cose pubbliche. Un'analisi che gli dà ragione
per fargli piacere lo manda in piazza con un argomento che la controparte smonta in trenta
secondi — e il danno è **suo**, davanti a tutti.

- **I fatti che indeboliscono la sua tesi hanno lo stesso rilievo di quelli che la
  rafforzano**: stessa posizione, stesso grassetto, mai in nota.
- **Vietate le formule da avvocato**: «avevi ragione tu», «la prova schiacciante», «lo scrive
  la fonte stessa a sostegno della tua tesi». Si scrive cosa dice la fonte, non da che parte sta.
- **La tesi avversaria si costruisce per intero, nella versione più forte**, prima di
  rispondere. Se non regge una risposta, si dice che non regge.
- **L'incertezza si dichiara**: fascia ≠ identità, correlazione ≠ causa, lordo ≠ netto,
  stima ≠ accertamento. Fra due stime divergenti, in pubblico si usa **la più prudente**.

Nata da un caso concreto (LIP RC Auto): avevo scritto «IVASS scrive nero su bianco quello che
sostieni tu», appoggiandomi a un margine per polizza che era **al lordo delle spese**.
L'inquadramento compiacente è venuto prima dell'errore tecnico e l'ha reso invisibile.

## 🥇 REGOLA D'ORO — il prompt non lascia spazio a invenzioni (21 agosto 2026)

Detta da Fernando: *«quello che dobbiamo imparare è scrivere prompt che non
lasciano spazio a invenzioni/aggiunte o altro a Meta»*, insieme a *«i prompt
devono essere minuziosi, non tralasciare nulla neanche la meno significativa;
con il sistema di copiarlo negli appunti non c'è bisogno di risparmiare
parole»*. È una regola d'ora di **attuazione**: vale ogni volta che si scrive
per far fare qualcosa a una macchina.

**La regola sotto tutte le altre: si descrive il DISEGNO, mai l'INTENZIONE.**
Ogni frase dev'essere verificabile guardando l'immagine finita.

- ⛔ «come chi chiude un rubinetto» è un'intenzione: il modello la interpreta, e
  interpretando **inventa**. 🟩 «il palmo guarda in basso; le quattro dita
  piegate a uncino, allineate; il pollice sotto, a fare da morsa; fra le dita e
  il palmo si vede un buco tondo; il polso ruotato in avanti» è un disegno.
- ⛔ Nominare un gesto culturale («il gesto dei soldi») lascia scegliere fra
  tre gesti diversi. 🟩 Si dice **quali dita si toccano e dove stanno le altre**.
- ⛔ «della stessa misura del riferimento» **non è una misura**. 🟩 Un rapporto
  fra due cose che si vedono nel disegno: «la figura è alta poco più di tre
  volte la larghezza degli occhiali».
- **Due cose che rischiano di somigliarsi si distinguono dentro il prompt**:
  «questa NON è la 134: là le dita si toccano per la punta, qui la mano avvolge
  e gira».
- **Se è già venuta sbagliata, si descrive l'errore**: dire alla macchina **come
  si riconosce lo sbaglio** funziona meglio di due richieste educate.
- **Non si salta un paragrafo perché sembra ovvio.** Il 21/08 ne avevo saltati
  quattro e sono tornate sbagliate **tre pose su quattro**, con esattamente i
  difetti che quei paragrafi vietano.

⚠️ E il controllo non è mai a occhio: *«va tutto verificato sempre»*, *«i numeri
non mentono»*. Lo stesso giorno l'occhio ha **approvato** una posa disegnata con
la testa il 19% più grande — invisibile ferma, evidentissima in movimento — e
**bocciato** un difetto che misurato non esisteva. Ogni consegna porta un numero
preso su qualcosa che sta nel file.

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

1. ⛔ **Il `/clear` non si propone mai.** Lo decide lui e basta. Il 20/08/2026
   aveva detto *«non farò più il clear»* dopo che una ripartenza era finita sul
   lavoro sbagliato; dal 21/08/2026 lo rifà, ma **solo perché adesso c'è il file
   di ripresa** che regge il filo al posto della conversazione (la procedura è
   qui sotto). Il divieto quindi resta su di me: non lo propongo, non lo
   suggerisco, non lo metto come opzione. Quando
   riprendo un lavoro e non ho il filo, **lo recupero io** dalle trascrizioni in
   `~/.claude/projects/-Users-osxssd-Desktop-ARCHIVIO-GENERALE-LAVORI-partecipazioneattiva/`,
   ordinate per **epoch** (`stat -f '%m %Sm'`: `31/07` come testo finisce sopra
   `19/08`). E un lavoro che si interrompe lascia un **punto di ripresa scritto
   in un file**, con la frase che **nomina il file** da aprire.

   **La regola del dopo clear** (21/08/2026, *«lo useremo come regola del
   dopo clear»*), diventata **procedura fissa il 21/08/2026**: *«quando ti dico
   faccio il clear tu sovrascrivi o aggiorni il file che andrai a rileggere dopo
   il clear»*. Funziona con **due parole d'ordine e un file solo**:

   - **`aggiorna file`** → sovrascrivo **`~/Desktop/ARCHIVIO GENERALE/Claude IA/RIPRESA.md`** con
     lo stato del lavoro in corso. E' **un file unico, sempre allo stesso
     percorso**: non se ne fanno copie con la data, perche' la frase di
     ripartenza deve poter essere sempre identica. Dentro, le **otto sezioni**:
     di che lavoro si tratta · le cose che non si toccano · dove stanno i file ·
     a che punto siamo · **il lavoro da fare adesso** · quello che si e' capito ·
     le trappole gia' pagate · come si consegna a Fernando. Le sue decisioni si
     citano **con le sue parole**. Poi carico negli appunti la frase fissa.
   - **La frase fissa**, sempre questa, mai un'altra:

         Leggi ~/Desktop/ARCHIVIO GENERALE/Claude IA/RIPRESA.md e riprendi da li'.

     E' la prima cosa che scrive quando riparte: la leggo **per intera** prima
     di rispondere, e da li' so cosa abbiamo fatto e a che punto siamo.

   ⚠️ Il file **si aggiorna anche senza che lui lo chieda**, quando un lavoro
   lungo cambia stato: se lui fa il clear e il file e' vecchio, la ripresa
   riparte dal punto sbagliato. E un messaggio lungo da incollare non si
   consegna piu': un messaggio e' fermo, un file si aggiorna.

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
7. **Le scoperte vanno negli script e nei manuali** (`~/Desktop/ARCHIVIO GENERALE/LAVORI/_MANUALI_CLAUDE`),
   non riderivate in conversazione.

Manuale completo: `~/Desktop/ARCHIVIO GENERALE/LAVORI/_MANUALI_CLAUDE/MANUALE_CREDITI_CLAUDE_v1.md`

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
