# Voce Wikidata — Partecipazione Attiva

Preparata il 28 luglio 2026. Tutto quello che si poteva fare senza il tuo account
è già fatto: fonti verificate, testi scritti, sigle controllate una per una
sull'API di Wikidata. **A te resta solo copiare e incollare.**

**A che serve.** Dire a Google — e alle intelligenze artificiali che oggi
rispondono al posto suo — che «partecipazione attiva» non è soltanto una frase
della lingua italiana: è anche un movimento preciso, con un portavoce, una sede,
un sito. È la leva più forte che avete, perché il nome è una locuzione comune ed è
il motivo per cui la ricerca sul vostro stesso nome rende così poco.

---

## Perché non posso farlo io

Creare un account e pubblicare a nome del movimento su una piattaforma esterna
sono le due cose che non faccio mai al posto tuo. Ho provato anche la scorciatoia
— **QuickStatements**, lo strumento che applica tutte le dichiarazioni in un colpo
solo — ma richiede un account **autoconfermato**, cioè con qualche giorno di vita
e un po' di modifiche alle spalle. Il tuo sarà nuovo, quindi oggi si va a mano.
(Il blocco pronto per quello strumento è in fondo, se un domani servirà.)

---

## Si può fare? Sì: le fonti ci sono

Wikidata accetta una voce se descrive un'entità reale con **fonti serie e
pubbliche**. Non bastano il vostro sito e i vostri social: servono fonti **di
terzi**. Ne avete due, che ho verificato leggendole:

| fonte | data | cosa dice |
|---|---|---|
| **Radio Radicale**, scheda 793958 | 10 luglio 2026 | archivia il convegno di Roma sulla legge elettorale: «Luigi Spanu, portavoce di Partecipazione Attiva», moderatore, insieme a Gherardo Colombo, Riccardo Magi, Dario Parrini, Carmela Auriemma, Christian Ferrari (CGIL) |
| **Articolo21**, firma di Roberto Zaccaria | 15 luglio 2026 | elenca «Partecipazione attiva (Spanu)» fra le organizzazioni della *Rete per un voto libero e uguale* |

Bastano: Radio Radicale è l'archivio di riferimento della politica italiana,
Articolo21 una testata registrata. Se in futuro escono altre citazioni sulla
stampa, dimmelo e le aggiungo: più fonti indipendenti, più la voce è al sicuro.

**Una raccomandazione seria.** Nel campo «descrivi brevemente la modifica», in
fondo alla pagina, scrivi che stai creando la voce del tuo movimento. Per esempio:

```
creo la voce del movimento di cui faccio parte, con fonti di stampa indipendenti
```

Non è vietato scrivere di sé. Nasconderlo è il modo più rapido per farsi
cancellare la voce.

---

# PASSO 1 — Creare l'account

1. Vai su **wikidata.org**
2. In alto a destra: **«Crea un'utenza»**
3. Servono un nome utente e una password. L'email è formalmente facoltativa:
   **mettila comunque**, è l'unico modo per recuperare l'accesso se si perde la
   password. Usare sempre l'indirizzo del webmaster:
   `webmaster.partecipazione.attiva@gmail.com` — mai una casella personale, o il
   giorno che cambia la persona si perde l'accesso alla voce.

# PASSO 2 — Creare la voce

Menu a sinistra → **«Crea un nuovo elemento»**. Compila i tre campi copiando
esattamente da qui.

**Lingua:** `it`

**Etichetta:**
```
Partecipazione Attiva
```

**Descrizione:** *(è la riga più importante di tutta la voce: è quella che
distingue il movimento dal significato comune delle parole)*
```
movimento civico italiano fondato nel 2021
```

**Alias** — si aggiungono uno per volta, con il pulsante «+»:
```
PA
```
```
Movimento Popolare dei Cittadini Italiani
```

Salva. In alto comparirà un codice tipo **Q123456789**. **Segnatelo e passamelo**:
mi serve per il passo 4.

# PASSO 3 — Aggiungere l'inglese

Nella voce appena creata, in alto, clicca **«Tutte le lingue inserite»** →
aggiungi:

- lingua `en`, etichetta `Partecipazione Attiva`
- descrizione `Italian civic political movement founded in 2021`

# PASSO 4 — Le dichiarazioni

Scendi a **«Dichiarazioni»** e clicca **«+ aggiungi dichiarazione»**. Ogni volta:
scrivi il nome della proprietà nella prima casella (comparirà nel menu a tendina),
poi il valore nella seconda.

I nomi qui sotto sono **esattamente** quelli che vedrai a schermo in italiano. Il
codice fra parentesi serve solo a confermare che hai scelto quella giusta.

| # | proprietà (come si chiama a schermo) | valore da scrivere |
|---|---|---|
| 1 | **istanza di** (P31) | `movimento politico` (Q2738074) |
| 2 | **istanza di** (P31) — stessa proprietà, secondo valore | `associazione` (Q48204) |
| 3 | **paese** (P17) | `Italia` (Q38) |
| 4 | **data di fondazione o creazione** (P571) | `2021` |
| 5 | **sito web ufficiale** (P856) | `https://partecipazione-attiva.it/` |
| 6 | **sede legale** (P159) | `Napoli` (Q2634) |
| 7 | **identificativo Facebook** (P2013) | `PartecipazioneAttiva21` |
| 8 | **nome utente TikTok** (P7085) | `partecipazione.at` |
| 9 | **identificativo YouTube di un canale** (P2397) | `UC8ItFAjkb61SwpyuSA5xIpw` |

**Se hai poco tempo, fai almeno la 1, la 3 e la 5**: bastano a rendere la voce
valida. Le altre si aggiungono quando vuoi, anche fra un mese.

*Sulla n. 9: YouTube mostra l'identificativo del canale solo dietro il banner dei
cookie, che non accetto per conto vostro. L'ha preso Fernando il 28 luglio 2026 da
`youtube.com/account_advanced`, campo «ID canale», e verificato a schermo: il
campo «ID utente» accanto riporta lo stesso codice senza il prefisso `UC`, che è
la prova che è quello giusto. Formato controllato: 24 caratteri, prefisso `UC`,
nessun carattere anomalo.*

# PASSO 5 — La fonte (fallo almeno sulla dichiarazione n. 1)

È la parte che protegge la voce dalla cancellazione. Sotto la dichiarazione
«istanza di → movimento politico» clicca **«+ aggiungi riferimento»**:

- proprietà: **URL di riferimento** (P854) → valore:
```
https://www.articolo21.org/2026/07/gia-pronti-decine-di-ricorsi-contro-la-legge-elettorale-ci-sara-una-grande-mobilitazione-clima-simile-al-referendum/
```
- poi «+» per aggiungere una seconda riga allo stesso riferimento: proprietà
  **consultato il** (P813) → valore `28 luglio 2026`

Se te la senti, ripeti con la seconda fonte:
```
https://www.radioradicale.it/scheda/793958/nuova-legge-elettorale-ultimo-atto-di-una-deriva-antidemocratica-gli-italiani-al-bivio
```

---

## Cosa NON mettere adesso

- **«partito politico»**: non lo siete ancora. Il giorno che presentate una lista
  o vi registrate, si aggiunge allora — la voce resta la stessa e cambia una riga.
- **Le persone** (presidente, portavoce): ognuna richiede una voce propria, che
  deve reggere da sola il requisito delle fonti. Semmai più avanti.

## Se qualcuno propone la cancellazione

Può succedere e non è un'accusa. Passamelo e rispondo io nella pagina di
discussione con le due fonti per esteso. Una voce con fonti di terzi verificabili
di solito resta.

---

# Quando hai finito: passami il codice Q

Il resto lo faccio io e chiude il cerchio:

1. Aggiungo il link Wikidata ai dati strutturati del sito (`sameAs`). Serve a
   legare le due identità nei due sensi: i marchi con **4 o più profili
   verificati** ottengono il pannello informativo di Google **4,1 volte più
   spesso**. Oggi ne avete 3 — Facebook, YouTube, TikTok: **Wikidata è il quarto**.
2. Aggiorno `llms.txt`, la scheda che il sito offre alle intelligenze artificiali.
3. Avviso Bing e Copilot con `python3 indexnow.py index.html`.

---

## Appendice — blocco per QuickStatements (solo quando l'account sarà confermato)

Da incollare su **quickstatements.toolforge.org**, modalità V1. I campi vanno
separati da TAB. Non serve oggi: è qui per non riscriverlo domani.

```
CREATE
LAST	Lit	"Partecipazione Attiva"
LAST	Len	"Partecipazione Attiva"
LAST	Dit	"movimento civico italiano fondato nel 2021"
LAST	Den	"Italian civic political movement founded in 2021"
LAST	Ait	"PA"
LAST	Ait	"Movimento Popolare dei Cittadini Italiani"
LAST	P31	Q2738074	S854	"https://www.articolo21.org/2026/07/gia-pronti-decine-di-ricorsi-contro-la-legge-elettorale-ci-sara-una-grande-mobilitazione-clima-simile-al-referendum/"	S813	+2026-07-28T00:00:00Z/11
LAST	P31	Q2738074	S854	"https://www.radioradicale.it/scheda/793958/nuova-legge-elettorale-ultimo-atto-di-una-deriva-antidemocratica-gli-italiani-al-bivio"	S813	+2026-07-28T00:00:00Z/11
LAST	P31	Q48204
LAST	P17	Q38
LAST	P571	+2021-00-00T00:00:00Z/9
LAST	P856	"https://partecipazione-attiva.it/"
LAST	P159	Q2634
LAST	P2013	"PartecipazioneAttiva21"
LAST	P7085	"partecipazione.at"
LAST	P2397	"UC8ItFAjkb61SwpyuSA5xIpw"
```

---

## Stato dei dati del sito

Già sistemato il 28 luglio 2026: i dati strutturati della home dichiaravano
**`PoliticalParty`** (partito politico) mentre la pagina Chi siamo dice «non siamo
un partito: siamo un movimento civico». Corretto in `Organization`, con
descrizione allineata.
