with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = '''    <div style="display:flex;flex-direction:column;gap:20px;">

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

    </div>'''

new = '''    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start;">

      <!-- FINESTRA 1: PENSATTIVO -->
      <div style="border-radius:16px;overflow:hidden;background:rgba(255,255,255,0.08);">
        <img src="images/pensattivo-rcauto.png" alt="PensAttivo RC Auto" style="width:100%;height:220px;object-fit:cover;object-position:top;display:block;">
        <div style="padding:12px 14px;">
          <div style="display:inline-block;background:#c0392b;color:#fff;font-size:.58em;font-weight:900;letter-spacing:2px;text-transform:uppercase;padding:3px 10px;border-radius:50px;margin-bottom:7px;">✊ Battaglia in corso</div>
          <div style="font-family:'Merriweather',serif;font-size:.88em;color:#fff;font-weight:700;line-height:1.3;margin-bottom:10px;">RC Auto: basta pagare di più solo perché sei del Sud</div>
          <a href="battaglie.html" style="display:inline-block;background:#c0392b;color:#fff;padding:6px 14px;border-radius:50px;text-decoration:none;font-size:.75em;font-weight:700;">Scopri →</a>
        </div>
      </div>

      <!-- FINESTRA 2: INSIEME PER NAPOLI -->
      <div style="border-radius:16px;overflow:hidden;background:rgba(255,255,255,0.08);">
        <img src="images/insieme-napoli.png" alt="Insieme per Napoli" style="width:100%;height:220px;object-fit:cover;object-position:top;display:block;">
        <div style="padding:12px 14px;">
          <div style="display:inline-block;background:#e8900a;color:#fff;font-size:.58em;font-weight:900;letter-spacing:2px;text-transform:uppercase;padding:3px 10px;border-radius:50px;margin-bottom:7px;">📍 Napoli</div>
          <div style="font-family:'Merriweather',serif;font-size:.88em;color:#fff;font-weight:700;line-height:1.3;margin-bottom:6px;">Insieme per Napoli</div>
          <div style="color:rgba(255,255,255,.82);font-size:.75em;margin-bottom:10px;"><strong style="color:#ffd580;">Neri · Cristiano · Ugon</strong></div>
          <a href="napoli.html" style="display:inline-block;background:#e8900a;color:#fff;padding:6px 14px;border-radius:50px;text-decoration:none;font-size:.75em;font-weight:700;">Scopri →</a>
        </div>
      </div>

    </div>'''

if old in html:
    html = html.replace(old, new)
    print("OK: finestre affiancate")
else:
    print("ERRORE: blocco non trovato")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Salvato")
