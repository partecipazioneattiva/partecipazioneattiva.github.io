import os

file = 'index.html'

anchor = '<section id="napoli" style="background:#fff3e0;padding:48px 32px;border-top:4px solid #e8900a;">'

sezione = '''<section id="perche-pa" style="background:#fff;padding:64px 32px;border-top:4px solid #f0f0f0;">
  <div style="max-width:1100px;margin:0 auto;">

    <!-- Titolo -->
    <div style="text-align:center;margin-bottom:48px;">
      <span style="background:#e8900a;color:#fff;font-size:.72em;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:4px 14px;border-radius:50px;">Perché Partecipazione Attiva</span>
      <h2 style="font-family:'Merriweather',serif;font-size:1.6em;color:#222;margin:16px 0 8px;">Non un altro partito.<br>Un movimento di cittadini veri.</h2>
      <p style="color:#666;font-size:.95em;max-width:520px;margin:0 auto;line-height:1.7;">Siamo nati dal basso, senza finanziatori occulti, senza carrieristi. Solo persone che vogliono cambiare le cose davvero.</p>
    </div>

    <!-- 3 valori -->
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-bottom:52px;">

      <!-- Valore 1 -->
      <div style="background:#fff8ee;border-radius:16px;padding:28px 24px;border-top:4px solid #e8900a;text-align:center;">
        <div style="font-size:2em;margin-bottom:12px;">✊</div>
        <div style="font-family:'Merriweather',serif;font-size:1em;font-weight:700;color:#222;margin-bottom:10px;">Battaglie concrete</div>
        <p style="font-size:.85em;color:#555;line-height:1.6;">Niente slogan vuoti. Ogni battaglia che sosteniamo ha un obiettivo preciso, misurabile e utile ai cittadini — come la lotta contro le discriminazioni territoriali sulle RC Auto.</p>
      </div>

      <!-- Valore 2 -->
      <div style="background:#fff8ee;border-radius:16px;padding:28px 24px;border-top:4px solid #8a4e00;text-align:center;">
        <div style="font-size:2em;margin-bottom:12px;">🏛️</div>
        <div style="font-family:'Merriweather',serif;font-size:1em;font-weight:700;color:#222;margin-bottom:10px;">Politica dal basso</div>
        <p style="font-size:.85em;color:#555;line-height:1.6;">Le decisioni le prendono i soci, non i capi. Ogni iscritto ha voce in capitolo. Siamo un movimento orizzontale, radicato nei territori, dalla Campania al Lazio.</p>
      </div>

      <!-- Valore 3 -->
      <div style="background:#fff8ee;border-radius:16px;padding:28px 24px;border-top:4px solid #27ae60;text-align:center;">
        <div style="font-size:2em;margin-bottom:12px;">🆓</div>
        <div style="font-family:'Merriweather',serif;font-size:1em;font-weight:700;color:#222;margin-bottom:10px;">Primo anno gratuito</div>
        <p style="font-size:.85em;color:#555;line-height:1.6;">Unirsi non costa nulla. Il primo anno è completamente gratuito: nessuna quota, nessun impegno. Provaci, conosci le persone, poi decidi tu.</p>
      </div>

    </div>

    <!-- Testimonianza -->
    <div style="background:linear-gradient(120deg,#8a4e00 0%,#e8900a 100%);border-radius:16px;padding:36px 40px;display:flex;align-items:center;gap:32px;flex-wrap:wrap;">
      <div style="font-size:3em;color:rgba(255,255,255,0.4);font-family:Georgia,serif;line-height:1;flex-shrink:0;">"</div>
      <div style="flex:1;min-width:220px;">
        <p style="font-family:'Merriweather',serif;font-size:1.05em;color:#fff;font-weight:700;line-height:1.6;margin-bottom:12px;">Mi sono iscritto perché finalmente ho trovato un movimento che parla dei problemi reali della gente comune, senza promesse impossibili.</p>
        <div style="font-size:.8em;color:rgba(255,255,255,.8);font-weight:600;">— Un iscritto di Napoli</div>
      </div>
      <a href="https://docs.google.com/forms/d/e/1FAIpQLSdUJHaPB9o6gA7TXHNLNgsKcftZjwCsjepZ3r_C9TH2ODsr3A/viewform" target="_blank" rel="noopener noreferrer" style="display:inline-block;background:#fff;color:#e8900a;padding:13px 28px;border-radius:50px;text-decoration:none;font-weight:900;font-size:.88em;white-space:nowrap;flex-shrink:0;">Iscriviti gratis →</a>
    </div>

  </div>
</section>

'''

with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

if anchor not in content:
    print('ERRORE: ancora non trovata')
else:
    content = content.replace(anchor, sezione + anchor)
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: sezione Perché PA inserita')
