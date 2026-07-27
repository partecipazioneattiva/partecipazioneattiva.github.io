"""Script dedicato per allineare stabilicum.html al testo approvato dalla Camera (16/07/2026).

Aggiorna SOLO:
1. Soglia premio di maggioranza: 40% -> 42%
2. Meccanismo ballottaggio -> proporzionale puro senza premio
3. Tetto seggi: 230/114 -> 220/113

Uso:
    python3 fix_stabilicum.py          # dry-run: mostra il diff delle righe cambiate
    python3 fix_stabilicum.py --apply  # applica le modifiche al file originale
"""
import difflib
import sys
from pathlib import Path

TARGET = Path(__file__).parent / "stabilicum.html"

REPLACEMENTS = [
    # --- Punto 1: soglia premio 40% -> 42% ---
    (
        "Alla coalizione che supera il 40% dei voti viene assegnato automaticamente un bonus",
        "Alla coalizione che supera il 42% dei voti viene assegnato automaticamente un bonus",
    ),
    (
        "al Senato. Significa che chi prende il 40% può arrivare a controllare ben oltre la",
        "al Senato. Significa che chi prende il 42% può arrivare a controllare ben oltre la",
    ),
    (
        "Sì — 70 dep. + 35 sen. al 40%<tr><td><strong>Preferenze</strong>",
        "Sì — 70 dep. + 35 sen. al 42%<tr><td><strong>Preferenze</strong>",
    ),
    (
        "Il costituzionalista Michele Ainis stima che una coalizione con il 40% dei voti",
        "Il costituzionalista Michele Ainis stima che una coalizione con il 42% dei voti",
    ),
    (
        "dei seggi con il 40% dei voti possa essere dichiarato incostituzionale.",
        "dei seggi con il 42% dei voti possa essere dichiarato incostituzionale.",
    ),

    # --- Punto 3: tetto seggi 230/114 -> 220/113 ---
    (
        "di 70 deputati e 35 senatori, entro un tetto massimo di 230 seggi alla Camera e 114\nal Senato.",
        "di 70 deputati e 35 senatori, entro un tetto massimo di 220 seggi alla Camera e 113\nal Senato.",
    ),

    # --- Punto 2: ballottaggio -> proporzionale puro senza premio ---
    (
        "<h3>3. Ballottaggio</h3><p>Se nessuna coalizione raggiunge il 40% e le prime due si collocano tra il 35% e il 40%,\n"
        "scatta un secondo turno tra sole due forze. Un ballottaggio nazionale — una novità assoluta\n"
        "per l'Italia.",
        "<h3>3. Proporzionale puro senza premio</h3><p>Se nessuna forza raggiunge il 42% dei voti, anche solo\n"
        "in una delle due Camere, o se Camera e Senato danno esiti divergenti, il premio di maggioranza\n"
        "non scatta e si applica il proporzionale puro, senza alcun bonus di seggi.",
    ),
    (
        "<tr><td><strong>Ballottaggio</strong><td>No<td>Sì — se nessuno al 40%",
        "<tr><td><strong>Proporzionale puro senza premio</strong><td>No<td>Sì — se nessuno al 42% o esiti Camera/Senato divergenti",
    ),
    (
        "<div class=domanda>Cosa succede se nessuno vince al primo turno?</div>"
        "<div class=risposta>Se le prime due coalizioni sono tra il 35% e il 40%, si va al ballottaggio.\n"
        "Un secondo voto tra le due sole forze più votate. I costituzionalisti segnalano\n"
        "un rischio tecnico: potrebbe succedere che alla Camera vinca una coalizione e\n"
        "al Senato un'altra — con due premi di governabilità per due schieramenti diversi,\n"
        "rendendo impossibile governare.</div></div>",
        "<div class=domanda>Cosa succede se nessuno vince al primo turno?</div>"
        "<div class=risposta>Non esiste un secondo turno. Se nessuna forza raggiunge il 42% dei voti, anche solo\n"
        "in una delle due Camere, oppure se Camera e Senato danno esiti divergenti, si applica\n"
        "il proporzionale puro senza premio: i seggi vengono assegnati in proporzione ai voti,\n"
        "senza bonus per nessuna coalizione.</div></div>",
    ),
]


def main():
    apply = "--apply" in sys.argv

    original = TARGET.read_text(encoding="utf-8")
    updated = original

    for old, new in REPLACEMENTS:
        count = updated.count(old)
        if count != 1:
            print(f"ERRORE: la stringa attesa e' stata trovata {count} volte (attesa: 1):")
            print(repr(old[:120]))
            sys.exit(1)
        updated = updated.replace(old, new)

    if updated == original:
        print("Nessuna modifica da applicare.")
        return

    old_lines = original.splitlines(keepends=True)
    new_lines = updated.splitlines(keepends=True)
    diff = difflib.unified_diff(old_lines, new_lines, fromfile="stabilicum.html (prima)", tofile="stabilicum.html (dopo)")
    diff_text = "".join(diff)
    print(diff_text)

    if apply:
        TARGET.write_text(updated, encoding="utf-8")
        print("\nFile aggiornato:", TARGET)
    else:
        print("\n[dry-run] Nessun file scritto. Rilancia con --apply per salvare.")


if __name__ == "__main__":
    main()
