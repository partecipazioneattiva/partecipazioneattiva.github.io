from pathlib import Path

F = Path("/Users/luigia/SITO-PA/mappa.html")
t = F.read_text(encoding="utf-8")

anchor = "    <strong>Adesioni e proposte:</strong>"
nuovo = ("    <strong>Contatti fra iscritti:</strong> chi ti scrive tramite il tasto &ldquo;Contatta&rdquo; "
         "<b>non vede la tua email</b>. Ricevi il messaggio e decidi tu: solo se accetti, vi scambiate gli "
         "indirizzi e da quel momento parlate direttamente fra voi (la Mappa non legge n&eacute; conserva la "
         "vostra conversazione). Puoi anche ignorare la richiesta o bloccare chi te l&rsquo;ha inviata.<br>\n"
         "    <strong>Adesioni e proposte:</strong>")

if "Contatti fra iscritti" in t:
    print("privacy: gia' aggiornata")
elif anchor in t:
    t = t.replace(anchor, nuovo, 1)
    F.write_text(t, encoding="utf-8")
    print("privacy: aggiunta la voce sui contatti fra iscritti")
else:
    raise SystemExit("STOP: sezione privacy non trovata")
