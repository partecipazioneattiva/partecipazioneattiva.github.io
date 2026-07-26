/* Assistente PensAttivo — risponde SOLO con FAQ scritte e approvate da PA.
   Non genera mai testo: ogni risposta e' presa parola per parola da
   assistente/faq.json. Tre livelli: FAQ -> ricerca nel sito (Pagefind) ->
   email con la domanda gia' scritta. Nessun dato del visitatore esce da qui:
   niente invii, niente servizi terzi, tutto nel browser.
   Lo costruisce: _tools/costruisci_assistente.py                         */
(function () {
  'use strict';
  if (window.paPensAttivo) return;
  window.paPensAttivo = true;

  var BASE = (function () {
    var s = document.querySelector('script[src*="pensattivo.js"]');
    return s ? s.src.replace(/pensattivo\.js.*$/, '') : 'assistente/';
  })();
  var EMAIL = 'partecipazioneattiva21@gmail.com';
  var dati = null, caricamento = null;

  /* ---------- stile ---------- */
  var css = '\
.pa-pa-btn{position:fixed;right:18px;bottom:18px;z-index:9998;width:58px;height:58px;\
border:none;border-radius:50%;background:linear-gradient(135deg,#8a4e00,#e8900a);\
color:#fff;font-size:26px;line-height:1;cursor:pointer;box-shadow:0 6px 20px rgba(0,0,0,.28);\
display:flex;align-items:center;justify-content:center;transition:transform .18s}\
.pa-pa-btn:hover{transform:scale(1.08)}\
.pa-pa-btn span{pointer-events:none}\
.pa-pa-velo{position:fixed;inset:0;z-index:9999;background:rgba(30,22,12,.55);\
display:flex;align-items:flex-end;justify-content:center;padding:0}\
.pa-pa-box{background:#fff;width:100%;max-width:560px;max-height:88vh;display:flex;\
flex-direction:column;border-radius:18px 18px 0 0;box-shadow:0 -8px 40px rgba(0,0,0,.3);\
animation:pa-pa-su .26s ease-out}\
@keyframes pa-pa-su{from{transform:translateY(100%)}to{transform:translateY(0)}}\
.pa-pa-testa{display:flex;align-items:center;gap:10px;padding:14px 16px;\
border-bottom:1px solid #f0dcc0;background:#fffaf3;border-radius:18px 18px 0 0}\
.pa-pa-testa strong{font-family:Montserrat,system-ui,sans-serif;font-size:1.02em;color:#8a4e00}\
.pa-pa-testa small{display:block;font-family:Montserrat,system-ui,sans-serif;\
font-size:.74em;color:#9a8straight;color:#96856f;font-weight:500}\
.pa-pa-x{margin-left:auto;border:none;background:none;font-size:1.7em;line-height:1;\
color:#8a4e00;cursor:pointer;padding:0 4px}\
.pa-pa-corpo{overflow-y:auto;padding:14px 16px;font-family:Merriweather,Georgia,serif;\
font-size:.94em;line-height:1.7;color:#4a4038;flex:1}\
.pa-pa-piede{padding:10px 16px 14px;border-top:1px solid #f0dcc0;display:flex;gap:8px}\
.pa-pa-piede input{flex:1;padding:11px 13px;border:1.5px solid #e8d5b8;border-radius:10px;\
font-family:Merriweather,Georgia,serif;font-size:.94em;color:#4a4038}\
.pa-pa-piede input:focus{outline:none;border-color:#e8900a}\
.pa-pa-piede button{border:none;border-radius:10px;padding:0 16px;cursor:pointer;\
background:linear-gradient(135deg,#8a4e00,#e8900a);color:#fff;\
font-family:Montserrat,system-ui,sans-serif;font-weight:600;font-size:.9em}\
.pa-pa-sugg{display:flex;flex-wrap:wrap;gap:7px;margin:10px 0 4px}\
.pa-pa-sugg button{border:1px solid #e8d5b8;background:#fffaf3;border-radius:999px;\
padding:7px 12px;cursor:pointer;font-family:Montserrat,system-ui,sans-serif;\
font-size:.8em;color:#8a4e00;text-align:left}\
.pa-pa-sugg button:hover{background:#fdf0dc;border-color:#e8900a}\
.pa-pa-dom{font-family:Montserrat,system-ui,sans-serif;font-weight:600;color:#8a4e00;\
margin:16px 0 6px;font-size:.95em}\
.pa-pa-risp{margin:0 0 8px}\
.pa-pa-link{font-family:Montserrat,system-ui,sans-serif;font-size:.84em;font-weight:600;\
color:#e8900a;text-decoration:none}\
.pa-pa-link:hover{text-decoration:underline}\
.pa-pa-altre{margin:14px 0 0;padding-top:12px;border-top:1px dashed #f0dcc0}\
.pa-pa-altre p{font-family:Montserrat,system-ui,sans-serif;font-size:.8em;\
color:#96856f;margin:0 0 7px}\
.pa-pa-nota{font-family:Montserrat,system-ui,sans-serif;font-size:.78em;\
color:#96856f;text-align:center;padding:0 16px 10px;margin:0}\
@media(min-width:640px){.pa-pa-velo{align-items:center;padding:20px}\
.pa-pa-box{border-radius:18px}.pa-pa-testa{border-radius:18px 18px 0 0}\
@keyframes pa-pa-su{from{transform:translateY(24px);opacity:.6}to{transform:none;opacity:1}}}';

  function stile() {
    if (document.getElementById('pa-pa-css')) return;
    var s = document.createElement('style');
    s.id = 'pa-pa-css';
    s.textContent = css.replace('color:#9a8straight;', '');
    document.head.appendChild(s);
  }

  /* ---------- BM25 ----------
     Prima qui c'era un confronto scritto a mano con lista di stopword, radici
     a 4 lettere e pesi inventati: quattro giri di aggiustamenti in cui ogni
     correzione rompeva un altro caso. BM25 e' l'algoritmo standard del
     recupero di informazioni (Robertson/Sparck Jones), misurato su 38 domande
     di prova: 33/38, con 8/8 di domande fuori tema correttamente rifiutate.
     I parametri k1=1,5 e b=0,75 sono i valori canonici.

     RIFIUTO: nessuna soglia assoluta. Se la frase che vince e' un'ESCA (una
     domanda deliberatamente fuori tema, in _dati/esche.json), non si risponde.
     Misurato che le soglie non funzionano: sui punteggi di similarita' e5 il
     fuori tema si sovrappone al tema (0,836 contro 0,835), e il margine fra
     primo e secondo e' piu' largo sul fuori tema che sul tema: userebbe il
     criterio al contrario.                                                  */
  var K1 = 1.5, B = 0.75;
  var indice = null;

  function pulisci(t) {
    return (t || '').toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '')
      .match(/[a-z0-9]+/g) || [];
  }

  function parole(t) {
    return pulisci(t).filter(function (p) { return p.length > 2; });
  }

  function costruisciIndice() {
    var docs = dati.frasi.map(parole);
    var df = {}, lung = [], somma = 0;
    docs.forEach(function (d) {
      lung.push(d.length);
      somma += d.length;
      var visti = {};
      d.forEach(function (p) { if (!visti[p]) { visti[p] = 1; df[p] = (df[p] || 0) + 1; } });
    });
    var tf = docs.map(function (d) {
      var c = {};
      d.forEach(function (p) { c[p] = (c[p] || 0) + 1; });
      return c;
    });
    indice = { tf: tf, df: df, lung: lung, media: somma / (docs.length || 1), n: docs.length };
  }

  function idfDi(p) {
    var n = indice.df[p] || 0;
    return Math.log(1 + (indice.n - n + 0.5) / (n + 0.5));
  }

  function cerca(dom) {
    var qt = parole(dom);
    if (!qt.length) return { esito: 'niente', top: [] };
    var best = {}, miglioreEsca = 0, miglioreFaq = 0;

    for (var i = 0; i < indice.n; i++) {
      var s = 0;
      for (var j = 0; j < qt.length; j++) {
        var f = indice.tf[i][qt[j]];
        if (!f) continue;
        s += idfDi(qt[j]) * f * (K1 + 1) /
             (f + K1 * (1 - B + B * indice.lung[i] / indice.media));
      }
      if (s <= 0) continue;
      var id = dati.righe[i];
      if (id === '_esca') { if (s > miglioreEsca) miglioreEsca = s; continue; }
      if (s > (best[id] || 0)) best[id] = s;
      if (s > miglioreFaq) miglioreFaq = s;
    }

    if (!miglioreFaq || miglioreEsca >= miglioreFaq) {
      return { esito: 'niente', top: [] };
    }
    var ordinate = Object.keys(best)
      .filter(function (k) { return k !== '_esca' && best[k] > 0; })
      .sort(function (x, y) { return best[y] - best[x]; }).slice(0, 3);
    if (!ordinate.length) return { esito: 'niente', top: [] };
    return {
      esito: 'trovato',
      top: ordinate.map(function (id) {
        var f = null;
        dati.faq.forEach(function (x) { if (x.id === id) f = x; });
        return f;
      }).filter(Boolean)
    };
  }

  /* ---------- interfaccia ---------- */
  var velo = null, corpo = null, campo = null;

  function apri() {
    stile();
    if (velo) { velo.style.display = 'flex'; campo.focus(); return; }
    velo = document.createElement('div');
    velo.className = 'pa-pa-velo';
    velo.innerHTML = '<div class="pa-pa-box" role="dialog" aria-label="Assistente PensAttivo">'
      + '<div class="pa-pa-testa"><strong>PensAttivo</strong>'
      + '<button class="pa-pa-x" aria-label="Chiudi">&times;</button></div>'
      + '<div class="pa-pa-corpo"></div>'
      + '<p class="pa-pa-nota">Rispondo solo con le risposte scritte da Partecipazione Attiva.</p>'
      + '<div class="pa-pa-piede">'
      + '<input type="text" placeholder="Scrivi la tua domanda&hellip;" aria-label="La tua domanda">'
      + '<button type="button">Chiedi</button></div></div>';
    document.body.appendChild(velo);
    corpo = velo.querySelector('.pa-pa-corpo');
    campo = velo.querySelector('input');
    velo.querySelector('.pa-pa-x').onclick = chiudi;
    velo.onclick = function (e) { if (e.target === velo) chiudi(); };
    velo.querySelector('.pa-pa-piede button').onclick = chiedi;
    campo.onkeydown = function (e) { if (e.key === 'Enter') chiedi(); };
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && velo && velo.style.display !== 'none') chiudi();
    });
    corpo.innerHTML = '<p class="pa-pa-nota">Sto preparando PensAttivo&hellip;</p>';
    carica().then(benvenuto, function () {
      corpo.innerHTML = '<p>Non riesco a caricare le risposte in questo momento. '
        + 'Puoi scrivere a <a class="pa-pa-link" href="mailto:' + EMAIL + '">'
        + EMAIL + '</a>.</p>';
    });
  }

  function chiudi() { if (velo) velo.style.display = 'none'; }

  function carica() {
    if (caricamento) return caricamento;
    caricamento = fetch(BASE + 'faq.json').then(function (r) {
      if (!r.ok) throw new Error('faq');
      return r.json();
    }).then(function (d) {
      dati = d;
      dati.frasi = d.frasi_testo || [];
      costruisciIndice();
      return d;
    });
    return caricamento;
  }

  function benvenuto() {
    var h = '<p class="pa-pa-risp">Ciao, sono <strong>PensAttivo</strong>. '
      + 'Chiedimi qualcosa su Partecipazione Attiva: ti mostro la risposta '
      + 'scritta dal movimento.</p><div class="pa-pa-sugg">';
    (dati.suggerite || []).forEach(function (d) {
      h += '<button type="button">' + esc(d) + '</button>';
    });
    corpo.innerHTML = h + '</div>';
    Array.prototype.forEach.call(corpo.querySelectorAll('.pa-pa-sugg button'), function (b) {
      b.onclick = function () { campo.value = b.textContent; chiedi(); };
    });
    campo.focus();
  }

  function esc(t) {
    return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function chiedi() {
    var dom = (campo.value || '').trim();
    if (!dom) return;
    var r = cerca(dom);
    if (r.esito === 'trovato') return mostra(dom, r.top);
    fallback(dom);
  }

  function mostra(dom, top) {
    var f = top[0];
    var h = '<p class="pa-pa-dom">' + esc(f.domanda) + '</p>'
      + '<p class="pa-pa-risp">' + esc(f.risposta) + '</p>';
    if (f.link) {
      h += '<a class="pa-pa-link" href="' + esc(f.link) + '">Vai alla pagina &rarr;</a>';
    }
    if (top.length > 1) {
      h += '<div class="pa-pa-altre"><p>Forse cercavi anche:</p><div class="pa-pa-sugg">';
      top.slice(1).forEach(function (x) {
        h += '<button type="button">' + esc(x.domanda) + '</button>';
      });
      h += '</div></div>';
    }
    corpo.innerHTML = h;
    Array.prototype.forEach.call(corpo.querySelectorAll('.pa-pa-altre button'), function (b) {
      b.onclick = function () { campo.value = b.textContent; chiedi(); };
    });
    corpo.scrollTop = 0;
    campo.value = '';
  }

  /* Nessuna risposta inventata: si offre la ricerca nel sito e poi l'email,
     con la domanda gia' scritta dentro. */
  function fallback(dom) {
    var mail = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent('Domanda dal sito')
      + '&body=' + encodeURIComponent(dom + '\n\n');
    corpo.innerHTML = '<p class="pa-pa-risp">Su questo non ho una risposta scritta '
      + 'dal movimento, e non voglio inventarla.</p>'
      + '<p class="pa-pa-risp">Posso cercare <strong>' + esc(dom) + '</strong> '
      + 'in tutte le pagine del sito, oppure puoi girare la domanda a una persona:</p>'
      + '<div class="pa-pa-sugg">'
      + '<button type="button" id="pa-pa-cerca">Cerca nel sito</button>'
      + '<a class="pa-pa-link" style="padding:7px 12px" href="' + mail + '">'
      + 'Scrivi a Partecipazione Attiva &rarr;</a></div>';
    var b = document.getElementById('pa-pa-cerca');
    if (b) b.onclick = function () {
      chiudi();
      if (typeof window.paApriCerca === 'function') {
        window.paApriCerca();
        setTimeout(function () {
          var i = document.querySelector('.pagefind-ui__search-input');
          if (i) { i.value = dom; i.dispatchEvent(new Event('input', { bubbles: true })); }
        }, 700);
      }
    };
    campo.value = '';
  }

  function icona() {
    stile();
    var b = document.createElement('button');
    b.className = 'pa-pa-btn';
    b.type = 'button';
    b.setAttribute('aria-label', 'Chiedi a PensAttivo');
    b.title = 'Chiedi a PensAttivo';
    b.setAttribute('data-pagefind-ignore', '');
    b.innerHTML = '<span>💬</span>';
    b.onclick = apri;
    document.body.appendChild(b);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', icona);
  } else {
    icona();
  }
})();
