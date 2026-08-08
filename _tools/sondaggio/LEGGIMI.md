# Il sondaggio dei sei appuntamenti di settembre

**8 agosto 2026.** Come funziona, e i due gesti che restano a Fernando.

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
