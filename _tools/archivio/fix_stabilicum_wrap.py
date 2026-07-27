"""Rimuove il </div> orfano che chiude prematuramente .article-wrap in stabilicum.html.

Il paragrafo "Il 1 aprile 2026..." termina con </p></div> subito prima di
"<p>Se ne parla ovunque". Quel </div> non ha un'apertura corrispondente nel
contesto (chiude article-wrap troppo presto) e va rimosso, lasciando il </p>.

Uso:
    python3 fix_stabilicum_wrap.py          # dry-run: mostra prima/dopo
    python3 fix_stabilicum_wrap.py --apply  # applica la modifica al file
"""
import sys
from pathlib import Path

TARGET = Path(__file__).parent / "stabilicum.html"

OLD = (
    "L&rsquo;iter si ferma per le festivit&agrave; pasquali</strong> e riprende nelle prossime settimane.</p></div><p>Se ne parla ovunque."
)
NEW = (
    "L&rsquo;iter si ferma per le festivit&agrave; pasquali</strong> e riprende nelle prossime settimane.</p><p>Se ne parla ovunque."
)


def count_div_balance(text: str) -> tuple[int, int]:
    start = text.find("<div class=article-wrap>")
    end = text.find("<div class=cta-finale>")
    segment = text[start:end]
    opens = segment.count("<div")
    closes = segment.count("</div>")
    return opens, closes


def main():
    apply = "--apply" in sys.argv

    original = TARGET.read_text(encoding="utf-8")

    count = original.count(OLD)
    if count != 1:
        print(f"ERRORE: la stringa attesa e' stata trovata {count} volte (attesa: 1):")
        print(repr(OLD))
        sys.exit(1)

    updated = original.replace(OLD, NEW)

    opens_before, closes_before = count_div_balance(original)
    opens_after, closes_after = count_div_balance(updated)

    print("--- Prima ---")
    print(OLD)
    print("\n--- Dopo ---")
    print(NEW)
    print(f"\nBilancio <div>/</div> nel blocco article-wrap -> cta-finale:")
    print(f"  Prima : {opens_before} aperti, {closes_before} chiusi")
    print(f"  Dopo  : {opens_after} aperti, {closes_after} chiusi")

    if apply:
        TARGET.write_text(updated, encoding="utf-8")
        print("\nFile aggiornato:", TARGET)
    else:
        print("\n[dry-run] Nessun file scritto. Rilancia con --apply per salvare.")


if __name__ == "__main__":
    main()
