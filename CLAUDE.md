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

## Consumo crediti (piano Pro) — vale SEMPRE, senza che l'utente lo chieda

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

## Sito

- HTML statico su GitHub Pages, **nessun template condiviso**: ogni pagina si porta
  dentro la propria copia del menu. Per cambiare il menu: `_tools/allinea_menu.py`.
- Rotazione card home → archivio: `_tools/ruota_home.py` (`--applica` per scrivere).
- Alcune voci di menu puntano a **sezioni della home**, non a pagine: contare i link
  entranti prima di rimuovere una sezione.
