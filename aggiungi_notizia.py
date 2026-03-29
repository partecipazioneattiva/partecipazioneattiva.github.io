import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

CARD = """
<!-- NOTIZIA IN EVIDENZA - Stabilicum -->
<section style="background:#fff3e0;padding:32px 32px 40px;border-top:4px solid #e8900a;border-bottom:4px solid #e8900a;">
  <div style="max-width:1100px;margin:0 auto;">
    <div style="display:inline-flex;align-items:center;gap:8px;background:#c0392b;color:#fff;font-family:'Montserrat',sans-serif;font-size:.72em;font-weight:900;letter-spacing:2px;text-transform:uppercase;padding:4px 14px;border-radius:50px;margin-bottom:20px;">
      📰 Attualità politica — 29 marzo 2026
    </div>
    <div style="display:grid;grid-template-columns:280px 1fr;gap:32px;align-items:center;">
      <a href="stabilicum.html" style="display:block;line-height:0;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.12);">
        <img src="images/pensattivo-stabilicum.jpg" alt="Pensattivo nella sezione elettorale — Stabilicum" style="width:100%;display:block;" loading="lazy">
      </a>
      <div>
        <h2 style="font-family:'Merriweather',serif;font-size:1.5em;font-weight:700;color:#8a4e00;line-height:1.35;margin-bottom:12px;">
          <a href="stabilicum.html" style="color:#8a4e00;text-decoration:none;">Stabilicum: la nuova legge elettorale spiegata ai cittadini</a>
        </h2>
        <p style="font-family:'Merriweather',serif;font-size:.92em;color:#555;line-height:1.7;margin-bottom:20px;">
          Da domani 31 marzo inizia l'esame parlamentare. Cos'è, come funziona, cosa cambia per chi vota.
          Un'analisi superpartes dal punto di vista del cittadino comune.
        </p>
        <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;">
          <a href="stabilicum.html" style="display:inline-block;background:#e8900a;color:#fff;padding:11px 28px;border-radius:50px;text-decoration:none;font-family:'Montserrat',sans-serif;font-weight:900;font-size:.85em;">Leggi l'analisi →</a>
          <span style="font-family:'Montserrat',sans-serif;font-size:.78em;color:#999;">⏱ 7 minuti di lettura</span>
        </div>
      </div>
    </div>
  </div>
</section>
<!-- FINE NOTIZIA IN EVIDENZA -->

"""

new_content = re.sub(
    r'(</section>)\s*(<section id="perche-pa")',
    r'\1\n' + CARD + r'\n\2',
    content,
    count=1
)

if new_content != content:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("OK: card notizia Stabilicum inserita in index.html")
else:
    print("ERRORE: nessuna modifica effettuata")
