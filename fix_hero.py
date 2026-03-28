with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = """    <div style="position:relative;">
      <div style="background:linear-gradient(135deg,#8a4e00,#e8900a);color:#fff;text-align:center;padding:10px 16px;font-family:'Montserrat',sans-serif;font-weight:900;font-size:.9em;letter-spacing:3px;text-transform:uppercase;border-radius:10px;margin-bottom:12px;">&#9679; Insieme per Napoli</div><a href="#napoli" style="display:block;"><img src="images/insieme-napoli.png" alt="Insieme per Napoli" style="width:100%;border-radius:16px;box-shadow:0 12px 48px rgba(0,0,0,0.35);"></a>
      <div style="position:absolute;bottom:16px;left:16px;right:16px;background:rgba(0,0,0,0.6);border-radius:10px;padding:12px 16px;text-align:center;">
        <div style="color:#f5a623;font-size:.7em;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">Prossime Amministrative - Napoli</div>
        <div style="color:#fff;font-weight:700;font-size:.9em;">Paolo Neri &bull; Antonio Cristiano &bull; Rosa Ugon</div>
      </div>
    </div>
  </div>
</section>"""

new = """  </div>
</section>"""

if old in html:
    html = html.replace(old, new)
    print("OK: blocco rimosso")
else:
    print("ERRORE: blocco non trovato")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html salvato")
