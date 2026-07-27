from pathlib import Path

F = Path("/Users/luigia/SITO-PA/pubblica_articolo.py")
t = F.read_text(encoding="utf-8")

if "data-pa-pin" in t:
    raise SystemExit("motore gia' corretto")

# --- 1) inserimento card: salta quelle pinnate ---
old = ("    # 1) trova la card attualmente in cima (prima ancora homepage-card) e inserisci la nuova prima\n"
       "    m = re.search(r'<a [^>]*data-pa-section=\"homepage-card\"', html)")
new = ("    # 1) inserisci la nuova card PRIMA della prima card NON pinnata.\n"
       "    #    Le card con data-pa-pin=\"1\" (es. la Mappa) restano sempre in cima.\n"
       "    m = re.search(r'<a (?![^>]*data-pa-pin)[^>]*data-pa-section=\"homepage-card\"', html)")

if old not in t:
    raise SystemExit("STOP: blocco inserimento card non trovato")
t = t.replace(old, new, 1)

# --- 2) pulizia badge: non toccare le card pinnate ---
old2 = "    return re.sub(r'<a [^>]*data-pa-section=\"homepage-card\".*?</a>', repl, html, flags=re.DOTALL)"
new2 = "    return re.sub(r'<a (?![^>]*data-pa-pin)[^>]*data-pa-section=\"homepage-card\".*?</a>', repl, html, flags=re.DOTALL)"

if old2 not in t:
    raise SystemExit("STOP: blocco pulisci_badge non trovato")
t = t.replace(old2, new2, 1)

F.write_text(t, encoding="utf-8")
print("pubblica_articolo.py corretto:")
print("  - le nuove card vanno DOPO quelle pinnate (Mappa resta prima)")
print("  - pulisci_badge_vecchi non tocca piu' le card pinnate")
