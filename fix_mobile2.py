file = 'index.html'

with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

errors = []

# 1. Bottoni hero su mobile: affiancati e non a tutta larghezza
# Aggiungo classe mob-btns ai bottoni hero
old1 = '<div style="display:flex;gap:14px;flex-wrap:wrap;">'
new1 = '<div class="mob-btns" style="display:flex;gap:14px;flex-wrap:wrap;">'
if old1 in content:
    content = content.replace(old1, new1, 1)
    print('OK 1: bottoni hero classe aggiunta')
else:
    errors.append('ERRORE 1: bottoni hero non trovati')

# 2. Banner prossimo evento: flex-wrap su mobile e font ridotto
old2 = '<div style="background:rgba(255,255,255,0.10);border-left:3px solid #ffd580;border-radius:8px;padding:9px 14px;margin-bottom:14px;display:flex;align-items:center;gap:10px;"><span style="font-size:.7em;background:#e8900a;color:#fff;font-weight:900;letter-spacing:1px;text-transform:uppercase;padding:3px 9px;border-radius:50px;white-space:nowrap;">&#128197; Prossimo evento</span><span style="font-size:.78em;color:#fff;font-weight:600;line-height:1.3;">Presentazione pubblica a <strong style="color:#ffd580;">Bagnoli, Napoli</strong> &mdash; data da confermare, seguici su Facebook</span></div>'
new2 = '<div class="mob-evento" style="background:rgba(255,255,255,0.10);border-left:3px solid #ffd580;border-radius:8px;padding:9px 14px;margin-bottom:14px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;"><span style="font-size:.7em;background:#e8900a;color:#fff;font-weight:900;letter-spacing:1px;text-transform:uppercase;padding:3px 9px;border-radius:50px;white-space:nowrap;">&#128197; Prossimo evento</span><span style="font-size:.78em;color:#fff;font-weight:600;line-height:1.3;">Presentazione pubblica a <strong style="color:#ffd580;">Bagnoli, Napoli</strong> &mdash; data da confermare, seguici su Facebook</span></div>'
if old2 in content:
    content = content.replace(old2, new2, 1)
    print('OK 2: banner prossimo evento aggiornato')
else:
    errors.append('ERRORE 2: banner prossimo evento non trovato')

# 3. Aggiungo regole CSS mobile per bottoni e sezione iscrizione
old_media = '  /* === RESPONSIVE MOBILE === */'
new_media = '''  /* === RESPONSIVE MOBILE === */
  /* Bottoni hero: compatti e affiancati */
  .mob-btns{flex-direction:row !important;flex-wrap:wrap !important;}
  .mob-btns a{padding:11px 20px !important;font-size:.82em !important;flex:0 0 auto !important;}

  /* Banner prossimo evento: badge su riga separata se necessario */
  .mob-evento{align-items:flex-start !important;}

  /* Sezione iscrizione: testo più piccolo, bottone non va a capo */
  .iscr-btns{flex-direction:column !important;gap:12px !important;}
  .iscr-btns a{text-align:center !important;white-space:normal !important;font-size:.82em !important;}
  .primo{white-space:normal !important;text-align:center !important;}
'''
if old_media in content:
    content = content.replace(old_media, new_media, 1)
    print('OK 3: CSS mobile aggiunto')
else:
    errors.append('ERRORE 3: blocco CSS mobile non trovato')

if errors:
    for e in errors:
        print(e)
else:
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
    print('FATTO — file salvato')
