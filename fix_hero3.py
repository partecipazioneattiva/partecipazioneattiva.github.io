with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Ripristina griglia 2 colonne nell'hero
old_grid = '  <div style="max-width:1100px;margin:0 auto;">\n    <div>'
new_grid = '  <div style="max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start;">\n    <div>'
if old_grid in html:
    html = html.replace(old_grid, new_grid)
    print("OK: griglia ripristinata")
else:
    print("WARN: griglia non trovata, potrebbe essere già ok")

# 2. Rimetti la colonna destra con 2 finestre impilate
old_end = '  </div>\n</section>\n\n<!-- SEZIONE IMPATTO'
new_right = '''    <div style="display:flex;flex-direction:column;gap:20px;">

      <!-- FINESTRA 1: PENSATTIVO -->
      <div style="position:relative;border-radius:16px;overflow:hidden;flex:1;">
        <img src="images/pensattivo-rcauto.png" alt="PensAttivo RC Auto" style="width:100%;height:260px;object-fit:cover;object-position:top;display:block;">
        <div style="position:absolute;inset:0;background:linear-gradient(to bottom,rgba(192,57,43,.75) 0%,rgba(0,0,0,.1) 60%,transparent 100%);"></div>
        <div style="position:absolute;top:0;left:0;right:0;padding:18px 20px;">
          <div style="display:inline-block;background:#c0392b;color:#fff;font-size:.62em;font-weight:900;letter-spacing:2px;text-transform:uppercase;padding:4px 12px;border-radius:50px;margin-bottom:8px;">✊ Battaglia in corso</div>
          <div style="font-family:'Merriweather',serif;font-size:1.05em;color:#fff;font-weight:700;line-height:1.3;text-shadow:0 2px 6px rgba(0,0,0,.4);margin-bottom:10px;">RC Auto: basta pagare di più solo perché sei del Sud</div>
          <a href="battaglie.html" style="display:inline-block;background:#c0392b;color:#fff;padding:7px 18px;border-radius:50px;text-decoration:none;font-size:.78em;font-weight:700;border:2px solid rgba(255,255,255,.5);">Scopri la battaglia →</a>
        </div>
      </div>

      <!-- FINESTRA 2: INSIEME PER NAPOLI -->
      <div style="position:relative;border-radius:16px;overflow:hidden;flex:1;">
        <img src="images/insieme-napoli.png" alt="Insieme per Napoli" style="width:100%;height:260px;object-fit:cover;object-position:center;display:block;filter:brightness(.55);">
        <div style="position:absolute;inset:0;background:linear-gradient(to top,rgba(138,78,0,.9) 0%,transparent 60%);"></div>
        <div style="position:absolute;bottom:0;left:0;right:0;padding:18px 20px;">
          <div style="display:inline-block;background:#e8900a;color:#fff;font-size:.62em;font-weight:900;letter-spacing:2px;text-transform:uppercase;padding:4px 12px;border-radius:50px;margin-bottom:8px;">📍 Napoli — Sede centrale</div>
          <div style="font-family:'Merriweather',serif;font-size:1.05em;color:#fff;font-weight:700;line-height:1.3;margin-bottom:6px;">Insieme per Napoli</div>
          <div style="color:rgba(255,255,255,.82);font-size:.8em;margin-bottom:10px;"><strong style="color:#ffd580;">Paolo Neri · Antonio Cristiano · Rosa Ugon</strong></div>
          <a href="napoli.html" style="display:inline-block;background:rgba(255,255,255,.15);border:2px solid rgba(255,255,255,.5);color:#fff;padding:7px 18px;border-radius:50px;text-decoration:none;font-size:.78em;font-weight:700;">Scopri il team →</a>
        </div>
      </div>

    </div>
  </div>
</section>

<!-- SEZIONE IMPATTO'''

if '  </div>\n</section>\n\n<!-- SEZIONE IMPATTO' in html:
    html = html.replace('  </div>\n</section>\n\n<!-- SEZIONE IMPATTO', new_right)
    print("OK: colonna destra aggiunta")
else:
    print("ERRORE: fine hero non trovata")

# 3. Rimuovi la sezione impatto a 2 colonne (background:#111)
old_impatto = '''<!-- SEZIONE IMPATTO: PENSATTIVO + INSIEME PER NAPOLI -->
<section style="background:#111;">
  <div style="max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;">

    <!-- SINISTRA: PENSATTIVO + BATTAGLIA -->
    <div style="position:relative;overflow:hidden;min-height:480px;">
      <img src="images/pensattivo-rcauto.png" alt="PensAttivo - RC Auto basta discriminazioni" style="width:100%;height:100%;object-fit:cover;object-position:top;display:block;">
      <div style="position:absolute;inset:0;background:linear-gradient(to bottom,rgba(192,57,43,.72) 0%,rgba(0,0,0,.15) 50%,transparent 100%);"></div>
      <div style="position:absolute;top:0;left:0;right:0;padding:28px 28px 0;">
        <div style="display:inline-block;background:#c0392b;color:#fff;font-size:.65em;font-weight:900;letter-spacing:3px;text-transform:uppercase;padding:5px 16px;border-radius:50px;margin-bottom:12px;">✊ Battaglia in corso</div>
        <div style="font-family:'Merriweather',serif;font-size:1.35em;color:#fff;font-weight:700;line-height:1.25;text-shadow:0 2px 8px rgba(0,0,0,.4);margin-bottom:12px;">RC Auto: basta pagare di più solo perché sei del Sud</div>
        <a href="battaglie.html" style="display:inline-block;background:#c0392b;color:#fff;padding:10px 22px;border-radius:50px;text-decoration:none;font-size:.82em;font-weight:700;border:2px solid rgba(255,255,255,.5);transition:all .2s;">Scopri la battaglia →</a>
      </div>
    </div>

    <!-- DESTRA: INSIEME PER NAPOLI -->
    <div style="position:relative;overflow:hidden;min-height:480px;">
      <img src="images/insieme-napoli.png" alt="Insieme per Napoli - Paolo Neri, Antonio Cristiano, Rosa Ugon" style="width:100%;height:100%;object-fit:cover;object-position:center;display:block;filter:brightness(.5);">
      <div style="position:absolute;inset:0;background:linear-gradient(to top,rgba(138,78,0,.9) 0%,transparent 60%);"></div>
      <div style="position:absolute;bottom:0;left:0;right:0;padding:32px;">
        <div style="display:inline-block;background:#e8900a;color:#fff;font-size:.65em;font-weight:900;letter-spacing:3px;text-transform:uppercase;padding:5px 16px;border-radius:50px;margin-bottom:14px;">📍 Napoli — Sede centrale</div>
        <div style="font-family:'Merriweather',serif;font-size:1.35em;color:#fff;font-weight:700;line-height:1.25;margin-bottom:10px;">Insieme per Napoli</div>
        <div style="color:rgba(255,255,255,.82);font-size:.85em;line-height:1.7;margin-bottom:18px;">I rappresentanti napoletani guidano la prima battaglia nazionale di Partecipazione Attiva.<br><strong style="color:#ffd580;">Paolo Neri · Antonio Cristiano · Rosa Ugon</strong></div>
        <a href="napoli.html" style="display:inline-block;background:rgba(255,255,255,.15);border:2px solid rgba(255,255,255,.5);color:#fff;padding:10px 22px;border-radius:50px;text-decoration:none;font-size:.82em;font-weight:700;">Scopri il team →</a>
      </div>
    </div>

  </div>
</section>'''

if old_impatto in html:
    html = html.replace(old_impatto, '')
    print("OK: sezione impatto rimossa")
else:
    print("ERRORE: sezione impatto non trovata")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Salvato")
