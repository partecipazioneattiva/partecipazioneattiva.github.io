content = open('index.html', 'r').read()

# ============================================================
# 1. BANNER ROSSO SOPRA LA TOPBAR
# ============================================================
old1 = '<div class="topbar">'
new1 = '''<div style="background:#c0392b;color:#fff;text-align:center;padding:10px 24px;font-family:\'Montserrat\',sans-serif;font-size:.82em;font-weight:700;letter-spacing:.5px;z-index:1000;">
  ✊ <strong>BATTAGLIA IN CORSO:</strong> RC Auto — basta discriminazioni territoriali. Napoli guida la lotta.
  &nbsp;·&nbsp;
  <a href="battaglie.html" style="color:#ffd580;text-decoration:underline;font-weight:900;">Scopri e sostieni →</a>
</div>
<div class="topbar">'''

if old1 in content:
    content = content.replace(old1, new1, 1)
    print('✅ Banner rosso aggiunto')
else:
    print('❌ Banner: topbar NON trovata')

# ============================================================
# 2. SEZIONE 2 COLONNE prima di section#napoli
# ============================================================
old2 = '<section id="napoli" style="background:#fff3e0;padding:48px 32px;border-top:4px solid #e8900a;">'
new2 = '''<!-- SEZIONE IMPATTO: PENSATTIVO + INSIEME PER NAPOLI -->
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
</section>

<section id="napoli" style="background:#fff3e0;padding:48px 32px;border-top:4px solid #e8900a;">'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print('✅ Sezione 2 colonne aggiunta')
else:
    print('❌ Sezione: testo NON trovato')

open('index.html', 'w').write(content)
