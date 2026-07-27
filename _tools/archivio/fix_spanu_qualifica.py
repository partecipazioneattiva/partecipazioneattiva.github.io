"""Uniforma la qualifica di Luigi Spanu nel box autore di stabilicum-nota-spanu-17lug2026.html.

Il box autore in alto riporta "Portavoce — Partecipazione Attiva", mentre la
firma in calce dice gia' "Portavoce nazionale — Partecipazione Attiva".
Aggiorna SOLO il box autore, senza toccare la firma in calce.

Uso:
    python3 fix_spanu_qualifica.py          # dry-run: mostra prima/dopo
    python3 fix_spanu_qualifica.py --apply  # applica la modifica al file
"""
import sys
from pathlib import Path

TARGET = Path(__file__).parent / "stabilicum-nota-spanu-17lug2026.html"

OLD = '<div class="ruolo">Portavoce &mdash; Partecipazione Attiva</div>'
NEW = '<div class="ruolo">Portavoce nazionale &mdash; Partecipazione Attiva</div>'


def main():
    apply = "--apply" in sys.argv

    original = TARGET.read_text(encoding="utf-8")

    count = original.count(OLD)
    if count != 1:
        print(f"ERRORE: la stringa attesa e' stata trovata {count} volte (attesa: 1):")
        print(repr(OLD))
        sys.exit(1)

    updated = original.replace(OLD, NEW)

    print("--- Prima ---")
    print(OLD)
    print("\n--- Dopo ---")
    print(NEW)

    if apply:
        TARGET.write_text(updated, encoding="utf-8")
        print("\nFile aggiornato:", TARGET)
    else:
        print("\n[dry-run] Nessun file scritto. Rilancia con --apply per salvare.")


if __name__ == "__main__":
    main()
