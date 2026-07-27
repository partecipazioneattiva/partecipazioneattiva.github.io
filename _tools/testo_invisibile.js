/* Cerca il testo che il lettore NON PUO' VEDERE: chiaro su fondo chiaro.
 *
 * Nasce da un caso vero (27/07/2026): in stabilicum-giugno2026.html e in
 * astensionismo-comunali2026.html un titolo portava color:#fff scritto nel
 * tag, avanzo di quando stava su una fascia scura. Le pagine sono poi state
 * rifatte con l'intestazione colorata (.article-hero) e quei titoli sono
 * rimasti bianchi sul fondo bianco: contrasto 1,04 su 1. Invisibili. Nessuno
 * li segnala proprio perche' nessuno li vede.
 *
 * PERCHE' IN JAVASCRIPT E NON IN PYTHON. Ci ho provato con un analizzatore
 * Python che leggeva gli attributi style e i fogli di stile: dava 55 allarmi
 * dove il browser ne trovava ZERO. Non basta leggere il codice, serve la
 * cascata vera (selettori discendenti, id, specificita', trasparenze
 * sovrapposte). L'unico strumento che sa calcolarla e' il browser.
 *
 * COME SI USA
 * 1. avviare il server locale (preview pa-site, porta 8899)
 * 2. incollare questo file nella console della pagina aperta
 * 3. await misuraContrasti(['index.html','ape.html', ...])
 *
 * DUE TRAPPOLE, gia' pagate:
 * - la cache: ricaricare la pagina NON ricarica il foglio di stile. Qui i
 *   <link> vengono riscritti con un ?v= nuovo dopo il caricamento, se no si
 *   misura la versione vecchia e si conclude "non funziona" per niente.
 * - gli sfondi trasparenti: rgba(255,255,255,.12) e' un velo di bianco al 12%
 *   su fondo scuro, non bianco pieno. Vanno sovrapposti uno sull'altro.
 */
async function misuraContrasti(pagine) {
  const lum = c => { const f = x => { x /= 255; return x <= .04045 ? x / 12.92 : Math.pow((x + .055) / 1.055, 2.4) };
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2]) };
  const contrasto = (a, b) => { const A = lum(a), B = lum(b); return (Math.max(A, B) + .05) / (Math.min(A, B) + .05) };
  const num = s => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(/[,\s\/]+/).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1] };
  const sopra = (s, g) => { if (!s) return g; const a = s[3]; if (a >= .999) return [s[0], s[1], s[2], 1];
    return [0, 1, 2].map(i => Math.round(s[i] * a + g[i] * (1 - a))).concat([1]) };

  const esito = [];
  for (const p of pagine) {
    const f = document.createElement('iframe');
    f.style.cssText = 'position:fixed;left:-9999px;width:1200px;height:900px';
    document.body.appendChild(f);
    await new Promise(r => { f.onload = r; f.onerror = r; f.src = '/' + p + '?v=' + Date.now(); setTimeout(r, 3000) });
    const d = f.contentDocument;
    // la cache serve il foglio di stile vecchio: si riscrivono gli href
    const link = [...d.querySelectorAll('link[rel=stylesheet]')];
    await Promise.all(link.map(l => new Promise(r => { const h = l.getAttribute('href');
      l.onload = r; l.onerror = r; l.setAttribute('href', h + (h.includes('?') ? '&' : '?') + 'v=' + Date.now()); setTimeout(r, 2000) })));
    await new Promise(r => setTimeout(r, 300));

    let sotto3 = 0; const gravi = [];
    for (const el of d.body.querySelectorAll('*')) {
      const testo = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join(' ').trim();
      if (testo.length < 3) continue;
      const s = getComputedStyle(el);
      if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) === 0) continue;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      let bg = [255, 255, 255, 1], immagine = false, e = el; const pila = [];
      while (e) { pila.push(e); e = e.parentElement }
      for (let i = pila.length - 1; i >= 0; i--) {
        const cs = getComputedStyle(pila[i]);
        if (cs.backgroundImage && cs.backgroundImage !== 'none') immagine = true;
        const c = num(cs.backgroundColor); if (c && c[3] > 0) bg = sopra(c, bg);
      }
      if (immagine) continue;              // testo su foto: si giudica a occhio
      const c = contrasto(sopra(num(s.color), bg), bg);
      if (c < 3) sotto3++;
      if (c < 1.6) gravi.push({ tag: el.tagName, testo: testo.slice(0, 60), contrasto: Math.round(c * 100) / 100 });
    }
    esito.push({ pagina: p, sotto3, gravi });
    f.remove();
  }
  console.table(esito.filter(x => x.gravi.length).flatMap(x => x.gravi.map(g => ({ pagina: x.pagina, ...g }))));
  return esito;
}
