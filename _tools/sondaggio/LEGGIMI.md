# Il sondaggio dei sei appuntamenti di settembre

**Aggiornato il 9 agosto 2026.**

> ## ⚠️ LEGGERE QUESTO PRIMA DEL RESTO
>
> **Dal 9 agosto la conferma via mail NON C'È PIÙ.** Chi vota, vota: il voto si
> conta subito.
>
> **Perché.** Nelle prime ore due persone hanno votato davvero, le mail di
> conferma sono state *consegnate* (verificato sul registro di Brevo), e
> **nessuna delle due ha cliccato**. Due su due. Quel passaggio non proteggeva:
> perdeva voti.
>
> **Effetto sulla riservatezza: migliora.** Prima l'indirizzo restava in chiaro
> fino al clic, o comunque 48 ore. Ora viene rimescolato all'istante e
> dell'originale non resta niente, mai, da nessuna parte.
>
> **Effetto sull'attendibilità: cala, e va detto.** Non si verifica più che
> l'indirizzo sia di chi lo scrive: chi insiste può inventarne altri. Il
> sondaggio è **indicativo** — dice dove va l'interesse, non proclama un
> vincitore. Per decidere l'ordine di sei incontri è il livello giusto.
>
> Le parti di questo foglio che parlano di «conferma», `sondaggio_pendenti` o
> `voto-confermato.html` descrivono **com'era**: restano perché le trappole che
> raccontano valgono ancora.

> ## 🆕 9 agosto, pomeriggio — LA PRIMA SCELTA
>
> Le sei caselle libere dicono **a quali temi la gente è interessata**, ma non
> li mettono in ordine: nei primi giorni davano **3-3-3-3-2-2**, cioè niente.
> Lo ha segnalato **Paolo Walter**, e i dati gli davano ragione.
>
> Da oggi, a chi segna **almeno due** temi compare una domanda in più:
> *«E se dovessi sceglierne uno solo, quale?»* — scelta singola, fra quelli
> che ha già segnato, e si può saltare. Chi ne segna **uno solo** non la vede:
> quel tema vale come prima scelta da sé.
>
> ### 🟥 NON è un ordine di uscita, e non va mai presentata così
>
> Ordine di Fernando, 9 agosto 2026: *«è categorico, non è una classifica
> d'uscita perché non lo sappiamo neanche noi i tempi che servono ad ogni tema
> per essere realizzato»*.
>
> Per questo la domanda dice **«se dovessi sceglierne uno solo»** e non «da
> quale cominciamo», e la pagina scrive per esteso che l'ordine dipende dal
> tempo di preparazione, che oggi non è noto. Se un domani si riscrive questa
> parte: **niente formule che promettano un calendario.**
>
> **Perché non la numerazione da 1 a 6**, che era la proposta di Paolo: le
> linee guida per i sondaggi di partecipazione civica raccomandano
> l'ordinamento **solo sotto le quattro-cinque voci**, e il **68%** del nostro
> pubblico arriva da telefono. Chi abbandona a metà non lascia una risposta
> parziale: non lascia niente. La domanda singola dà la stessa graduatoria al
> prezzo di un tocco.
>
> Pezzi nuovi: **`10_prima_scelta.sql`** (colonna `voti_primo`, vista e
> funzione a quattro argomenti) e **`11_togli_la_prova_del_primo.sql`**.
> La funzione `02` passa `p_primo`.
>
> **Installato e verificato il 9 agosto 2026, 13:45-13:55.** La verifica è
> stata fatta in tre tempi, e vale come metodo:
> 1. una richiesta volutamente incoerente (tema `ape`, prima scelta `mappa`)
>    → risponde `primo_non_valido`: prova che il codice nuovo è quello in
>    funzione, **senza lasciare voti**;
> 2. un voto vero con un indirizzo finto → `mappa` segna `voti_primo 1`:
>    prova che la catena sito → funzione → archivio regge fino in fondo;
> 3. `11_togli_la_prova_del_primo.sql` → i conteggi tornano ai valori di
>    partenza (5 persone, 3-3-3-3-2-2, `voti_primo` a zero).
>
> ⚠️ Il passo 1 da solo **non basta**: rifiuta prima di arrivare all'archivio,
> quindi non direbbe niente su una funzione con la firma sbagliata.

Come funziona, e i gesti che restano a Fernando.

---

## Cosa fa, in una frase

Chi arriva sul sito — anche per la prima volta, senza iscriversi — sceglie i
temi che gli interessano fra i sei di settembre, lascia **solo la sua email**,
riceve una mail e conferma con un clic. **Il voto conta solo dopo quel clic**,
e in quel preciso momento **l'indirizzo viene cancellato**.

---

## Perché è fatto così

Il problema di partenza: *anonimo per chi vota, ma non uno che vota cento volte*.

Anonimato totale e «una persona un voto» **non stanno insieme**: se non chiedo
niente, non posso sapere che sei già passato. E bloccare per indirizzo di rete
è peggio del male — in Italia gli operatori mobili fanno passare migliaia di
clienti dallo stesso indirizzo, e **il 68% del nostro pubblico arriva da
telefono**: avremmo bloccato loro, non i furbi.

La mail risolve tutto, a patto di **non tenerla**:

| momento | cosa esiste | dove |
|---|---|---|
| invio del voto | l'indirizzo in chiaro | tabella `sondaggio_pendenti`, max 48 ore |
| clic di conferma | il voto contato + un'impronta illeggibile | `sondaggio_conteggio`, `sondaggio_impronte` |
| **subito dopo** | **l'indirizzo è cancellato** | — |

L'impronta è `sha256(segreto + indirizzo)`. Il segreto **se lo genera il
database da solo** (32 byte casuali) e non esce mai da lì: non è in questo
repository, non è passato per nessuna chat, non lo conosce nessuno. Senza il
segreto l'impronta non si può ricondurre a un indirizzo nemmeno da parte nostra.

### Cosa NON si può fare, e va detto

Chi ha molte caselle di posta può votare più volte, una per casella. Non c'è
rimedio che non passi dal chiedere un documento. È il livello di serietà giusto
per decidere l'ordine di sei incontri.

---

## I pezzi

| pezzo | dove sta | cosa fa |
|---|---|---|
| `01_archivio.sql` | qui | tabelle, viste e le due funzioni del database |
| `02_funzione_sondaggio.ts` | qui | riceve il voto e manda la mail con Brevo |
| sondaggio | `settembre-2026-appuntamenti.html#sondaggio` | il modulo che si vede |
| pagina di arrivo | `voto-confermato.html` | conta il voto e mostra i risultati |
| invito | striscia nell'apertura della home | porta al sondaggio |

Brevo è lo **stesso canale** che il sito usa già per le conferme della Mappa:
non è stato aggiunto nessun servizio nuovo.

---

## ⚙️ I DUE GESTI CHE RESTANO A FERNANDO

Servono i suoi accessi, e per questo non posso farli io.

### 1 · L'archivio dati — due minuti

1. apri **supabase.com** → il progetto di Partecipazione Attiva
2. menu a sinistra → **SQL Editor** → **New query**
3. incolla **tutto** il contenuto di `01_archivio.sql`
4. **Run** (in basso a destra)

Deve rispondere `Success`. Si può rilanciare senza danni: è scritto per non
rifare due volte le stesse cose.

### 2 · La funzione che manda la mail — cinque minuti

1. stesso pannello → menu a sinistra → **Edge Functions**
2. **Deploy a new function** → nome **esattamente**: `sondaggio`
3. cancella il codice di esempio e incolla tutto `02_funzione_sondaggio.ts`
4. **Deploy**

⚠️ **Un controllo prima di deployare:** nello stesso pannello, in
**Edge Functions → Secrets**, deve già esistere la chiave di Brevo (la usano le
funzioni della Mappa). La funzione la cerca sotto quattro nomi:
`BREVO_API_KEY`, `BREVO_KEY`, `SENDINBLUE_API_KEY`, `BREVO`.
**Se il nome è un altro, dimmelo e cambio una riga** — non serve che tu copi la
chiave da nessuna parte.

---

## Come si prova che funziona

1. apri `settembre-2026-appuntamenti.html#sondaggio`
2. scegli due temi, metti **il tuo** indirizzo, spunta l'informativa, invia
3. deve arrivare una mail da *Partecipazione Attiva*
4. clicca **Conferma il mio voto**: si apre `voto-confermato.html` e i numeri
   compaiono
5. riprova con lo **stesso** indirizzo: deve rispondere *«hai già votato»*

Se al passo 3 non arriva niente: pannello → Edge Functions → `sondaggio` →
**Logs**. Se dice `manca il segreto della chiave Brevo`, è il caso del nome
diverso qui sopra.

---

## Quando il sondaggio finisce

I numeri sono anonimi e restano. Le impronte non servono più:

```sql
drop table sondaggio_impronte;
```

Da quel momento del sondaggio non resta traccia di nessuno — solo i conteggi.

---

## Le quattro trappole pagate l'8 agosto 2026

Messe qui perché non si ripaghino, e perché tre su quattro **non erano nel
codice ma nell'ambiente**.

**1 · Chrome traduce il codice.** Il pannello di Supabase in italiano fa
tradurre anche il contenuto dell'editor: `begin` diventava `inizio`, `end`
diventava `FINE`, `sondaggio_impronte` diventava `sondaggi o_impronte`.
Prima di incollare qualunque cosa: **disattivare la traduzione per
supabase.com** (icona 文A nella barra dell'indirizzo → «Non tradurre mai»).

**2 · Le liste come argomento.** Passare un elenco come `text[]` faceva
rispondere `42883 — No function matches the given name and argument types`.
Il ponte fra funzioni e archivio (PostgREST) non sempre abbina una lista JSON
a quel tipo. **Si passa `jsonb`** e si converte dentro. Corretto in
`03_correzione_temi.sql`.

**3 · `digest()` non sta in `public`.** Su Supabase pgcrypto vive nel reparto
`extensions`. Una funzione con `set search_path = public` non lo trova e dà
lo stesso `42883`. **Serve `set search_path = public, extensions`.**
Corretto in `04_digest.sql`.

  ⚠️ Nota di metodo: lo stesso guasto dava **due errori diversi** secondo chi
  chiamava. Il sito riceveva «permission denied» (il controllo dei permessi
  viene prima di entrare nella funzione), il server riceveva `42883`. Per due
  volte ho diagnosticato dalla porta sbagliata. **Si legge il registro della
  funzione, non si deduce dal sintomo esterno.**

**4 · Le chiavi di Supabase sono cambiate nel 2026.** `SUPABASE_SERVICE_ROLE_KEY`
è dichiarata obsoleta (nel pannello compare come DEPRECATED). Le nuove —
`SUPABASE_SECRET_KEYS` e `SUPABASE_PUBLISHABLE_KEYS` — **non sono stringhe ma
elenchi JSON**, da cui si prende la voce `default`. La funzione ora prova
prima la nuova e poi ripiega sulla vecchia, così regge anche quando le vecchie
verranno spente a fine 2026.

**E una quinta, che è un consiglio.** Una chiave Brevo generata nuova rispose
`401 Key not found`. Invece di indagare, si è usata `BREVO_KEY`, quella che
manda le mail della Mappa dall'11 luglio: **quando esiste già un pezzo che
funziona, si usa quello.**

### Per provare senza aspettare

Il blocco anti-doppione tiene fermo lo stesso indirizzo per dieci minuti. Per
fare prove in fila si usa il segno più:
`webmaster.partecipazione.attiva+p1@gmail.com` arriva nella stessa casella ma
per l'archivio è un indirizzo diverso.

---

## ⚙️ Come si controlla la funzione PRIMA di installarla

Sul Mac c'è **Deno**, lo stesso motore che esegue le funzioni su Supabase.
Quindi non serve installare al buio e vedere che succede:

```bash
deno check ~/Desktop/LAVORI/partecipazioneattiva/_tools/sondaggio/02_funzione_sondaggio.ts
```

Se dice solo `Check ...` senza altro, il codice è valido. Si può anche
avviarla davvero e interrogarla in locale:

```bash
deno run --allow-net --allow-env _tools/sondaggio/02_funzione_sondaggio.ts
curl -s -X POST http://localhost:8000 -H 'Content-Type: application/json' \
  -d '{"temi":["ape"],"email":"prova@esempio.it"}'
```

Senza i segreti risponde `nessuna chiave server disponibile`: è la risposta
giusta, e dimostra che parte e ragiona.

**Stesso discorso per gli <script> dentro le pagine:** si estrae il contenuto
e gli si passa `node --check`. L'8 agosto 2026 una parentesi di troppo in
`voto-confermato.html` ha lasciato la pagina ferma su «Un momento...» — e
sarebbe bastato questo controllo, che dura un secondo.

## ⚠️ Niente lettere accentate nel codice della funzione

L'editor di Supabase rovina i caratteri accentati incollati: nelle mail si
leggeva `√® tuo` invece di `è tuo`, `gi√†` invece di `già`. Il file ora è
**tutto ASCII** e usa le forme HTML (`&egrave;`, `&rsquo;`, `&mdash;`), che
non si possono rompere. **Se un domani si riscrive qualcosa, si continua
così.** Il testo scritto dalle persone non ha questo problema: arriva dal
browser e non passa mai dall'editor.
