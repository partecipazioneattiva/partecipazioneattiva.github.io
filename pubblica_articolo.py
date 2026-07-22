#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
#  PUBBLICA_ARTICOLO.PY  —  motore unico di pubblicazione sito PA
#  Per ogni nuovo articolo: compila SOLO il blocco CONFIG qui sotto e lancia:
#      python3 /Users/luigia/SITO-PA/pubblica_articolo.py
#  Fa: articolo da GOLD (spanu-sire.html) + card in cima + badge automatico
#  per data + voce ticker + riga sitemap + 8 check. Idempotente (assert).
#  NON tocca aggiorna_feed/pagefind/git: quelli restano nel comando di push.
# ============================================================================
import re, json, sys, os

BASE = os.path.dirname(os.path.abspath(__file__)) + '/'

# Anagrafica autori: chiave -> (Nome, Ruolo, foto). Aggiungere qui se serve.
AUTORI = {
    'spanu':    ('Luigi Spanu',  'Portavoce', 'images/organigramma/luigi-spanu.webp'),
    'neri':     ('Paolo Neri',   'Direttivo', 'images/organigramma/paolo-neri.webp'),
    'nicotra':  ('Angelo Nicotra','Presidente','images/organigramma/angelo-nicotra-finale.webp'),
    'cristiano':('Antonio Cristiano','Direttivo','images/organigramma/antonio-cristiano.webp'),
    'mollica':  ('Amilcare Mollica','Consulente legale','images/organigramma/amilcare-mollica.webp'),
    'pa':       ('Partecipazione Attiva','Documento di posizione','LOGO-PA.webp'),
}

BODY_LEGGE = '''
<style>
.pa-tbl{width:100%;border-collapse:collapse;margin:22px 0;font-family:montserrat,sans-serif;font-size:.86em}
.pa-tbl th,.pa-tbl td{border:1px solid #f0e6d3;padding:9px 12px;text-align:left;vertical-align:top}
.pa-tbl thead th{background:#8a4e00;color:#fff;font-weight:700}
.pa-tbl tbody th{background:#fff8ee;color:#8a4e00;font-weight:700}
.pa-tbl caption{caption-side:bottom;text-align:left;font-size:.82em;color:#888;padding-top:8px;line-height:1.5}
.pa-stat{display:flex;flex-wrap:wrap;gap:14px;margin:26px 0}
.pa-stat .s{flex:1 1 220px;background:#fff8ee;border-radius:12px;padding:18px 20px}
.pa-stat .n{font-family:merriweather,serif;font-size:2em;font-weight:900;line-height:1;color:#8a4e00}
.pa-stat .n.ok{color:#2e7d32}
.pa-stat .l{font-size:.82em;color:#555;margin-top:6px;font-family:montserrat,sans-serif;line-height:1.5}
.pa-dl{display:flex;align-items:center;gap:16px;border:2px solid #e8900a;border-radius:14px;padding:20px 22px;margin:30px 0;background:#fff8ee}
.pa-dl .ico{flex:0 0 auto;width:46px;height:46px;border-radius:10px;background:#8a4e00;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:.72em;font-family:montserrat,sans-serif}
.pa-dl .t{flex:1 1 auto;font-family:montserrat,sans-serif;font-size:.84em;color:#555;line-height:1.5}
.pa-dl .t b{color:#8a4e00;display:block;margin-bottom:3px}
.pa-dl a.btn{flex:0 0 auto;background:#e8900a;color:#fff;text-decoration:none;padding:11px 20px;border-radius:50px;font-family:montserrat,sans-serif;font-weight:700;font-size:.84em}
.pa-qa{background:#fafafa;border:1px solid #f0e6d3;border-radius:12px;padding:16px 20px;margin:0 0 14px}
.pa-qa .q{font-family:montserrat,sans-serif;font-weight:700;color:#8a4e00;margin-bottom:7px}
.pa-qa p{margin:0!important;font-size:.95em!important}
@media(max-width:768px){
 .pa-tbl thead{position:absolute;left:-9999px}
 .pa-tbl tr{display:block;border:1px solid #f0e6d3;border-radius:10px;padding:8px 12px;margin-bottom:14px}
 .pa-tbl tbody th{display:block;background:#8a4e00;color:#fff;border:none;border-radius:6px;margin-bottom:4px}
 .pa-tbl td{display:block;border:none;border-bottom:1px solid #f5ece0;padding:7px 0 7px 42%;position:relative}
 .pa-tbl td:last-child{border-bottom:none}
 .pa-tbl td::before{content:attr(data-l);position:absolute;left:0;top:7px;width:38%;font-weight:700;color:#8a4e00;font-size:.9em}
}
</style>

<article class="article-wrap">

<div class="box-info" style="border-left-color:#8a4e00">
<strong>Il criterio</strong>
Una legge elettorale &egrave; giusta solo se la accetteresti senza sapere in anticipo se vincerai o perderai: dev&rsquo;essere riconosciuta e applicata <strong>sia al miglior amico sia al peggior nemico</strong>. Se la scriveresti diversamente a seconda di chi comanda, non &egrave; una regola: &egrave; un&rsquo;arma.
</div>

<p>La legge elettorale determina le condizioni con cui il popolo, titolare della sovranit&agrave;, concorre alla formazione delle assemblee parlamentari. Non &egrave; una legge come le altre: tocca l&rsquo;eguaglianza del voto, la libert&agrave; di scelta e l&rsquo;equilibrio tra i poteri. Per questo va giudicata con un criterio pi&ugrave; severo di qualsiasi tecnicismo &mdash; e proprio ora, mentre in aula si discute una riforma e le elezioni si avvicinano.</p>

<h2>I cinque requisiti</h2>
<p>Una regola che superi quel test deve tenere insieme cinque esigenze, oggi trattate come se fossero in conflitto: <strong>rappresentanza</strong> (il Parlamento rispecchia il Paese reale); <strong>vera scelta dei cittadini</strong> (l&rsquo;elettore sceglie la persona, non ratifica una lista decisa altrove); <strong>governabilit&agrave;</strong> (dal voto esce una maggioranza in grado di governare); <strong>nessun ricatto al governo</strong> (nessun piccolo alleato diventa indispensabile e detta le condizioni); <strong>nessun abuso del governo sul Parlamento</strong> (chi vince non pu&ograve; da solo impadronirsi degli organi di garanzia e delle regole del gioco).</p>
<p>L&rsquo;errore delle riforme italiane &egrave; usare un solo strumento, il premio di maggioranza, per fare tutto. Un premio grande produce abuso; un premio legato alla coalizione produce ricatto. La soluzione giusta separa due domande diverse: <strong>chi mi rappresenta</strong> (la formula elettorale) e <strong>come si stabilizza il governo</strong> (la forma di governo). Che siano due leve distinte &egrave; uno degli orientamenti pi&ugrave; consolidati della letteratura comparata (Sartori; Lijphart; Shugart-Carey).</p>

<table class="pa-tbl">
<caption>Formula, forma di governo, durata dei governi e proporzionalit&agrave; (indice di Gallagher, valori indicativi). Fonti: EPRS/Consiglio europeo e Pew Research/ParlGov per la durata; dataset di M. Gallagher (Trinity College Dublin) e Casal B&eacute;rtoa per l&rsquo;indice.</caption>
<thead><tr><th>Paese</th><th>Formula</th><th>Forma di governo</th><th>Durata governi</th><th>Gallagher</th></tr></thead>
<tbody>
<tr><th>Germania</th><td data-l="Formula">Proporz. personalizzato (MMP)</td><td data-l="Forma di governo">Sfiducia costruttiva</td><td data-l="Durata">Alta (~10 anni)</td><td data-l="Gallagher">~3&ndash;5</td></tr>
<tr><th>Spagna</th><td data-l="Formula">Proporzionale (D&rsquo;Hondt)</td><td data-l="Forma di governo">Sfiducia costruttiva</td><td data-l="Durata">Medio-alta</td><td data-l="Gallagher">~5&ndash;6</td></tr>
<tr><th>Svezia</th><td data-l="Formula">Proporzionale (Sainte-Lagu&euml;)</td><td data-l="Forma di governo">Parlamentarismo negativo</td><td data-l="Durata">Medio-alta</td><td data-l="Gallagher">~1&ndash;3</td></tr>
<tr><th>Portogallo</th><td data-l="Formula">Proporzionale (D&rsquo;Hondt)</td><td data-l="Forma di governo">Governo respinto solo a magg. assoluta</td><td data-l="Durata">Medio-alta</td><td data-l="Gallagher">~4&ndash;6</td></tr>
<tr><th>Italia</th><td data-l="Formula">Misto (attuale)</td><td data-l="Forma di governo">Sfiducia semplice</td><td data-l="Durata">Bassa (premier &lt; 2 anni)</td><td data-l="Gallagher">~4</td></tr>
</tbody>
</table>
<p>Dove esiste un meccanismo forte di forma di governo, i governi durano pur restando i sistemi proporzionali. La stabilit&agrave; dipende dalla forma di governo, non dalla distorsione della rappresentanza.</p>

<h2>Cosa vogliamo, cosa chiediamo subito</h2>
<p>Distinguiamo la visione piena (che in parte richiede revisione costituzionale) da ci&ograve; che &egrave; possibile ottenere subito con legge ordinaria. Il &laquo;subito&raquo; non tradisce il &laquo;vogliamo&raquo;: &egrave; la prima tappa dello stesso percorso.</p>
<table class="pa-tbl">
<thead><tr><th>Requisito</th><th>Cosa vorremmo</th><th>Cosa chiediamo subito</th></tr></thead>
<tbody>
<tr><th>Scelta della persona</th><td data-l="Vorremmo">Preferenze piene o sistema misto</td><td data-l="Subito">Collegi piccoli e liste corte</td></tr>
<tr><th>Governabilit&agrave;</th><td data-l="Vorremmo">Stabilit&agrave; dalla forma di governo</td><td data-l="Subito">Premio eventuale con tetto sotto i 3/5</td></tr>
<tr><th>Nessun abuso</th><td data-l="Vorremmo">Garanzie + quorum presidenziale protetto</td><td data-l="Subito">Tetto sotto i 3/5: nessuno tocca da solo Consulta e CSM</td></tr>
<tr><th>Nessun ricatto</th><td data-l="Vorremmo">Sfiducia costruttiva (art. 94)</td><td data-l="Subito">Premio ripartito in proporzione ai voti</td></tr>
<tr><th>Diritti di chi perde</th><td data-l="Vorremmo">Statuto opposizioni in Costituzione</td><td data-l="Subito">Statuto opposizioni per legge</td></tr>
</tbody>
</table>

<h2>Il tetto sotto i 3/5: perch&eacute; esattamente 3/5</h2>
<p>&Egrave; il punto tecnicamente pi&ugrave; rilevante, e il pi&ugrave; frainteso. Il tetto <strong>non &egrave; un numero scelto a caso</strong>: &egrave; derivato dalla Costituzione. I tre quinti sono il quorum con cui il Parlamento in seduta comune elegge gli organi di garanzia &mdash; i giudici costituzionali di nomina parlamentare (l. cost. 2/1967) e i membri laici del CSM (l. 195/1958). Ne segue una regola limpida: <strong>una maggioranza che resti sotto i 3/5 non pu&ograve; eleggere da sola quegli organi.</strong> Qualsiasi altro numero sarebbe arbitrario; 3/5 no.</p>

<div class="pa-stat">
<div class="s"><div class="n">&minus;8</div><div class="l">Con il sistema vigente, nel 2022 il centrodestra arriv&ograve; a 8 seggi dai 3/5 in seduta comune (352 su 600).</div></div>
<div class="s"><div class="n ok">+48</div><div class="l">Con la nostra proposta, la stessa coalizione resta a 48 seggi dai 3/5 (312 su 600): margine strutturale, non fortuna.</div></div>
</div>

<h2>Il premio: quanto piccolo, in numeri</h2>
<p>Il premio <strong>non &egrave; il modello ideale</strong>: &egrave; un compromesso transitorio, necessario finch&eacute; &mdash; senza sfiducia costruttiva &mdash; la governabilit&agrave; dipende anche dalla legge elettorale. Per questo lo si vincola, invece di ampliarlo. Lo definiamo per esito: si attiva solo sopra il <strong>40%</strong> dei voti; porta la coalizione vincente a circa il <strong>52%</strong> dei seggi; non supera mai il <strong>55%</strong> (estero e regioni speciali inclusi), restando sotto i 3/5; e se il proporzionale d&agrave; gi&agrave; una maggioranza, non scatta affatto.</p>
<p>La soglia del 40% &egrave; una scelta, non un difetto: se nel Paese esiste una maggioranza netta, il premio la consolida; se non esiste, il sistema non la inventa &mdash; la costruisce il Parlamento.</p>

<h2>La verifica sui dati reali (2022)</h2>
<p>Non un&rsquo;affermazione, ma un calcolo. Applicando la proposta ai risultati del 2022, il centrodestra (43,8% dei voti) otterrebbe 193 seggi col solo proporzionale e 208 (52%) con il premio &mdash; ben sotto i 240 dei 3/5. La rappresentanza resta preservata: l&rsquo;indice di disproporzionalit&agrave; di Gallagher del riparto &egrave; <strong>5,58</strong>, valore tipico dei sistemi proporzionali.</p>

<div class="pa-dl">
<div class="ico">XLSX</div>
<div class="t"><b>Simulazione 2022 &mdash; foglio di calcolo</b>Riparto seggio per seggio (metodo Hare), test del premio, analisi di sensibilit&agrave; e indice di Gallagher. Formule verificabili: cambiando gli input, il modello si ricalcola.</div>
<a class="btn" href="/Simulazione_APE_2022.xlsx" download>Scarica</a>
</div>

<p>L&rsquo;analisi di sensibilit&agrave; mostra che l&rsquo;esito &egrave; stabile: la soglia (38&ndash;42%) nel 2022 fa scattare il premio in ogni caso, e il tetto (54&ndash;56%) tiene la maggioranza sotto i 3/5 in ogni scenario. Gli organi di garanzia sono protetti per costruzione, non per fortuna elettorale.</p>

<h2>Principali obiezioni e risposte</h2>
<div class="pa-qa"><div class="q">&laquo;Il premio &egrave; incoerente col proporzionale.&raquo;</div><p>Non &egrave; il modello ideale: &egrave; un compromesso transitorio, dichiarato come tale. Finch&eacute; manca la sfiducia costruttiva, la governabilit&agrave; dipende anche dalla legge elettorale; per questo il premio si vincola, non si amplia. Nella visione piena sparisce, sostituito dalla forma di governo.</p></div>
<div class="pa-qa"><div class="q">&laquo;Con il 40% il premio non scatta quasi mai.&raquo;</div><p>&Egrave; una scelta, non un difetto: se non esiste una maggioranza netta, il sistema non deve inventarla. La simulazione mostra per&ograve; che nel 2022 sarebbe scattato, e la sensibilit&agrave; che l&rsquo;esito &egrave; stabile tra il 38% e il 42%.</p></div>
<div class="pa-qa"><div class="q">&laquo;Il tetto al 55% &egrave; un&rsquo;auto-limitazione eccessiva.&raquo;</div><p>&Egrave; il cuore del test dell&rsquo;amico e del nemico. Il limite &egrave; giustificato perch&eacute; derivato dai 3/5 con cui la Costituzione elegge gli organi di garanzia. Percepirlo come troppo rigido significa guardarlo dal punto di vista di chi vince &mdash; quello che la proposta rifiuta.</p></div>
<div class="pa-qa"><div class="q">&laquo;Il riparto del premio favorisce le liste-civetta.&raquo;</div><p>Obiezione risolta: il premio si ripartisce solo tra le liste che superano da sole il 3%, e la salvaguardia trasferisce i voti senza dare seggi di premio. Spacchettarsi in micro-liste riduce la quota, non la aumenta.</p></div>
<div class="pa-qa"><div class="q">&laquo;Il metodo &mdash; senza fiducia, con voto largo &mdash; &egrave; irrealistico.&raquo;</div><p>&Egrave; un criterio di legittimazione, non una previsione. La Commissione di Venezia raccomanda proprio ampio consenso e stabilit&agrave; delle regole nell&rsquo;anno che precede il voto. Il documento fissa lo standard; la sua difficolt&agrave; misura la distanza dell&rsquo;attuale prassi da quello standard.</p></div>

<h2>Chi scrive le regole</h2>
<p>Il metodo imparziale non affida il testo n&eacute; a chi ha la posta in gioco n&eacute; a chi non ha gli strumenti tecnici. Distingue tre ruoli: <strong>i cittadini fissano i requisiti</strong> (il &laquo;cosa&raquo;, insindacabile); <strong>i tecnici traducono in testo</strong> e devono dimostrare che regge al vaglio della Corte (il &laquo;come&raquo;); <strong>il vaglio pubblico verifica</strong> clausola per clausola, in chiaro. &Egrave; la stessa filosofia dell&rsquo;Assemblea Popolare: i cittadini pongono la domanda e obbligano le istituzioni a rispondere in modo motivato; la competenza scrive e ne risponde.</p>

<div class="box-info">
<strong>In una frase</strong>
Nel breve accettiamo un filo meno di premio in cambio di un sistema che nessuno ha interesse a far saltare &mdash; e le garanzie che oggi chiediamo per gli altri sono quelle che domani varranno per noi. Una legge elettorale &egrave; legittima solo se sopravvive al test dell&rsquo;amico e del nemico, nel merito e nel metodo.
</div>

</article>
'''


# -*- coding: utf-8 -*-
# Incollare SUBITO SOPRA la riga  ART = {  in pubblica_articolo.py
# e impostare 'body' : BODY_PENSATTIVO

BODY_PENSATTIVO = '''
<style>
.pa-hero-img{display:block;max-width:300px;width:60%;margin:0 auto 28px;border-radius:18px;box-shadow:0 10px 30px rgba(0,0,0,.15)}
.pa-lead{font-size:1.12em!important;color:#8a4e00!important;font-weight:600}
.pa-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:20px;margin:28px 0}
.pa-card{border:1px solid #f0e6d3;border-radius:14px;overflow:hidden;background:#fff;text-decoration:none;display:flex;flex-direction:column;transition:transform .15s,box-shadow .15s}
.pa-card:hover{transform:translateY(-3px);box-shadow:0 10px 26px rgba(0,0,0,.10)}
.pa-card img{width:100%;height:150px;object-fit:cover;display:block}
.pa-card .b{padding:14px 16px}
.pa-card .cat{font-family:montserrat,sans-serif;font-size:.7em;font-weight:900;letter-spacing:1.5px;text-transform:uppercase;color:#e8900a;margin-bottom:5px}
.pa-card .t{font-family:merriweather,serif;font-size:1em;color:#333;line-height:1.4;font-weight:700}
</style>

<article class="article-wrap">

<img class="pa-hero-img" src="images/pensattivo-astensionismo.webp" alt="PensAttivo, la mascotte aliena di Partecipazione Attiva">

<p class="pa-lead">Avrai gi&agrave; visto questo omino verde in giro per il sito. &Egrave; ora di presentarlo: si chiama <strong>PensAttivo</strong>, e s&igrave;, &egrave; un alieno.</p>

<h2>Perch&eacute; proprio un alieno</h2>
<p>Immagina un marziano appena atterrato in Italia. Osserva gli umani discutere di politica e resta perplesso: molti non guardano <em>cosa</em> si propone, ma <em>chi</em> lo propone. Se lo dice la mia squadra &egrave; giusto; se lo dice l&rsquo;altra &egrave; sbagliato &mdash; a prescindere. Come tifare per una maglietta invece che per un&rsquo;idea.</p>
<p>PensAttivo non capisce questo tifo, perch&eacute; viene da fuori. E proprio perch&eacute; viene da fuori vede una cosa semplice che a noi, presi dalla partita, spesso sfugge: <strong>una proposta &egrave; buona o cattiva per quello che dice, non per la casacca di chi la firma.</strong></p>

<div class="box-info">
<strong>&#x1F47D; Il punto di vista dell&rsquo;alieno</strong>
Chi vuole cambiare le cose in modo giusto, senza tifoseria di squadra, alla fine assomiglia a un marziano: guarda gli stessi fatti che vediamo tutti, ma senza il filtro del &laquo;da che parte stai&raquo;. &Egrave; scomodo, a volte fa sorridere. Ma &egrave; l&rsquo;unico sguardo che non ti frega.
</div>

<h2>Non &egrave; solo una simpatica mascotte</h2>
<p>Dietro la battuta c&rsquo;&egrave; il metodo di Partecipazione Attiva. Lo stesso sguardo &laquo;da fuori&raquo; di PensAttivo &egrave; il criterio con cui valutiamo ogni battaglia: <strong>la accetteresti anche se a governare fosse chi non voti?</strong> Se una regola ti va bene solo quando comanda la tua parte, non &egrave; una regola giusta: &egrave; un&rsquo;arma. Se invece regge comunque &mdash; con l&rsquo;amico e con l&rsquo;avversario &mdash; allora &egrave; solida.</p>
<p>Ecco perch&eacute; PensAttivo compare accanto ai nostri temi: RC Auto, sanit&agrave;, legge elettorale, astensionismo. Non &egrave; un logo decorativo. &Egrave; il promemoria, in forma di alieno verde, che su ogni questione proviamo a ragionare cos&igrave;: guardando i fatti, non le bandiere.</p>

<h2>La regola di PensAttivo</h2>
<p>Se dovessimo riassumere il personaggio in una frase, sarebbe questa:</p>

<div class="box-comunicato">
<div class="label">&#x1F47D; In una frase</div>
<p>Prima di dire &laquo;giusto&raquo; o &laquo;sbagliato&raquo;, togliti la maglietta della squadra e guarda i fatti da alieno. Poi decidi.</p>
</div>

<h2>Dove trovi PensAttivo</h2>
<p>Il nostro alieno ha gi&agrave; preso posizione su diverse battaglie. Ecco dove lo trovi al lavoro:</p>

<div class="pa-grid">
<a class="pa-card" href="rcauto-neopatentati-giugno2026.html">
  <img loading="lazy" src="images/pensattivo-rcauto.webp" alt="PensAttivo e la RC Auto">
  <div class="b"><div class="cat">RC Auto</div><div class="t">Perch&eacute; a Napoli si paga di pi&ugrave; a parit&agrave; di rischio</div></div>
</a>
<a class="pa-card" href="stabilicum-aula-camera-giugno2026.html">
  <img loading="lazy" src="images/pensattivo-stabilicum.webp" alt="PensAttivo e la riforma elettorale">
  <div class="b"><div class="cat">Riforma elettorale</div><div class="t">Cosa cambia per chi vota con la nuova legge</div></div>
</a>
<a class="pa-card" href="sanitapubblica.html">
  <img loading="lazy" src="images/pensattivo-sanita.webp" alt="PensAttivo e la sanit&agrave; pubblica">
  <div class="b"><div class="cat">Sanit&agrave; pubblica</div><div class="t">Liste d&rsquo;attesa e diritto alle cure</div></div>
</a>
<a class="pa-card" href="astensionismo.html">
  <img loading="lazy" src="images/pensattivo-astensionismo.webp" alt="PensAttivo e l&rsquo;astensionismo">
  <div class="b"><div class="cat">Astensionismo</div><div class="t">Perch&eacute; sempre meno persone vanno a votare</div></div>
</a>
</div>

<p>PensAttivo continuer&agrave; a spuntare accanto alle nostre battaglie. Ogni volta che lo vedi, &egrave; un invito: <strong>guarda i fatti, non la maglietta.</strong></p>

</article>
'''

# ============================== CONFIG ARTICOLO =============================
# Incollare SUBITO SOPRA la riga  ART = {  in pubblica_articolo.py
# e impostare 'body' : BODY_CAVALLEGGERI

BODY_CAVALLEGGERI = '''
<style>
.pa-hero-img{display:block;max-width:100%;border-radius:18px;box-shadow:0 10px 30px rgba(0,0,0,.15);margin:0 0 28px}
.pa-lead{font-size:1.12em!important;color:#8a4e00!important;font-weight:600}
.pa-fig{margin:32px 0}
.pa-fig img{width:100%;border-radius:14px;box-shadow:0 6px 20px rgba(0,0,0,.12)}
.pa-fig figcaption{font-family:montserrat,sans-serif;font-size:.82em;color:#9c5b00;margin-top:10px;text-align:center;font-style:italic}
.pa-box{background:#fff8ee;border:2px solid #ffd580;border-radius:16px;padding:24px 28px;margin:28px 0}
.pa-box h3{font-family:montserrat,sans-serif;color:#9c5b00;font-size:1em;font-weight:800;text-transform:uppercase;letter-spacing:.5px;margin:0 0 10px}
</style>

<article class="article-wrap">

<img class="pa-hero-img" src="images/cavalleggeri-museo.webp" alt="Rendering del progetto: corridoio di murales lungo Via Marco Polo a Cavalleggeri d'Aosta, Fuorigrotta">

<p class="pa-lead">Un rione di Fuorigrotta pu&ograve; diventare un museo a cielo aperto &mdash; e con l&rsquo;America&rsquo;s Cup 2027 alle porte, il momento &egrave; adesso.</p>

<p>Partecipazione Attiva propone al Comune di Napoli e alla Municipalit&agrave; 10 un progetto di rigenerazione urbana attraverso l&rsquo;arte: trasformare Via Marco Polo e il Rione Cavalleggeri d&rsquo;Aosta in un percorso di murales che racconti l&rsquo;identit&agrave; del quartiere, ne rafforzi il decoro e la sicurezza percepita, e lo colleghi idealmente al waterfront di Bagnoli, a due passi dalla fermata della Linea 2.</p>

<div class="pa-fig">
<img src="images/cavalleggeri-oggi.webp" alt="Un edificio reale di Via Marco Polo con muro cieco, oggi">
<figcaption>Oggi: facciate cieche e anonime lungo un asse ad altissimo passaggio pedonale &mdash; scuole, negozi, la metro a due fermate.</figcaption>
</div>

<h2>Perch&eacute; proprio qui</h2>
<p>Cavalleggeri d&rsquo;Aosta &egrave; tra le zone meglio collegate della citt&agrave;: fermata Linea 2, Cumana, numerose linee di bus, alta concentrazione di scuole e attivit&agrave; di prossimit&agrave;. Un intervento qui ha una ricaduta reale e visibile, non confinata a un pubblico di soli residenti. Il quartiere ha inoltre un patrimonio identitario da raccontare, dalla memoria dell&rsquo;edilizia popolare ai segni della dismessa funivia Fuorigrotta&ndash;Posillipo.</p>

<h2>L&rsquo;occasione: America&rsquo;s Cup 2027</h2>
<p>Nel 2027 Napoli ospiter&agrave; la 38&ordf; edizione dell&rsquo;America&rsquo;s Cup, con le basi dei team a Bagnoli, quartiere immediatamente adiacente. Cavalleggeri d&rsquo;Aosta &egrave; la naturale soglia di accesso tra la metro e il waterfront: un museo diffuso qui estenderebbe i benefici dell&rsquo;evento anche a un quartiere che, come tanti, resta spesso escluso dalle ricadute dirette dei grandi eventi.</p>

<div class="pa-fig">
<img src="images/cavalleggeri-piazza.webp" alt="Rendering della strada pedonalizzata con murale del golfo di Napoli e della funivia">
<figcaption>La visione: strada pedonalizzata, alberi, panchine &mdash; e le facciate che raccontano la memoria del quartiere.</figcaption>
</div>

<h2>Non solo estetica: una leva economica e di servizio</h2>
<p>Il museo diffuso non cancella la vita economica del rione: la valorizza. Il mercato di Via Marco Polo &mdash; commercio popolare vivo e servizio di prossimit&agrave; per le famiglie &mdash; diventa una tappa del percorso, non un elemento da nascondere. Rigenerare qui significa banchi ordinati, spazio curato, pi&ugrave; passaggio: non sgombero del popolare.</p>

<div class="pa-fig">
<img src="images/cavalleggeri-mercato.webp" alt="Rendering del mercato di Via Marco Polo rigenerato, con murale sullo sfondo">
<figcaption>Il mercato di Via Marco Polo in una piazza rigenerata, circondata dalle opere del percorso.</figcaption>
</div>

<div class="pa-box">
<h3>Il nodo burocratico</h3>
<p>I murales sono legalmente manutenzione straordinaria (Consiglio di Stato, sent. 1289/2023): servono permessi edilizi. La Regione Campania finanzia la creativit&agrave; urbana con la L.R. 3/2023 (200.000&euro;/anno), ma per accedervi il Comune di Napoli deve prima adottare un regolamento comunale e iscrivere le superfici nell&rsquo;Albo regionale. &Egrave; il passaggio che chiediamo di sbloccare.</p>
</div>

<p>Il modello a cui guardiamo &egrave; quello sperimentato con successo a Ponticelli dal collettivo INWARD: programmi di creativit&agrave; urbana condotti con la partecipazione delle comunit&agrave; residenti, capaci di trasformare complessi popolari anonimi in distretti artistici e poli di attrazione.</p>

<img src="images/cavalleggeri-fumetto.webp" alt="Fumetto PensAttivo: PensAttivo ti porta a Cavalleggeri" style="width:100%;border-radius:14px;margin:32px 0;box-shadow:0 6px 20px rgba(0,0,0,.12)">

<p class="pa-lead">Nessun quartiere &egrave; di serie B. Il fascicolo completo &egrave; stato presentato al Comune di Napoli, alla Municipalit&agrave; 10 e, per conoscenza, alla Regione Campania.</p>

</article>
'''

BODY_MAPPA = '''
<style>
.pa-lead{font-size:1.12em!important;color:#8a4e00!important;font-weight:600}
.pa-box{background:#fff8ee;border:2px solid #ffd580;border-radius:16px;padding:24px 28px;margin:28px 0}
.pa-cta{background:#fff8ee;border:2px solid #ffd580;border-radius:16px;padding:28px 32px;margin:36px 0;text-align:center}
.pa-cta p{font-family:merriweather,serif;color:#333;font-size:1.1em;font-weight:700;margin-bottom:16px}
.pa-cta a{display:inline-block;background:#e8900a;color:#fff;text-decoration:none;padding:14px 32px;border-radius:50px;font-family:montserrat,sans-serif;font-weight:700;font-size:.95em}
</style>

<p class="pa-lead">C\u2019\u00e8 una frase che in ogni assemblea civica torna sempre, uguale a s\u00e9 stessa: \u201cIl problema \u00e8 che siamo divisi. Bisognerebbe fare rete.\u201d</p>

<p>La si dice, tutti annuiscono, e poi ognuno torna nel proprio gruppo. Alla riunione successiva la frase ricompare, identica. \u00c8 una diagnosi che tutti condividono e che nessuno ha mai tradotto in uno strumento.</p>

<p>Non \u00e8 ipocrisia. \u00c8 che <strong>manca l\u2019infrastruttura</strong>. Non sappiamo nemmeno chi c\u2019\u00e8.</p>

<h2>Il disarmo delle competenze</h2>

<p>Il danno non \u00e8 astratto. Si misura ogni volta che un comitato di cittadini si oppone a una decisione amministrativa e perde.</p>

<p>Chi ha attraversato quelle battaglie lo sa: un gruppo civico non possiede, o possiede solo in parte, gli strumenti di conoscenza che rendano qualificata e fattibile una proposta alternativa. Contestare una delibera richiede dati tecnici, competenze acquisite, capacit\u00e0 di leggere un progetto. Senza quelle, la protesta resta protesta \u2014 e viene archiviata.</p>

<p>Il punto \u00e8 che quelle competenze esistono. C\u2019\u00e8 un ingegnere in pensione a due isolati. C\u2019\u00e8 un\u2019avvocata che si occupa di diritto amministrativo nello stesso quartiere. C\u2019\u00e8 chi sa leggere un bilancio comunale, chi ha lavorato in una ASL, chi conosce l\u2019urbanistica.</p>

<p>Ma le tematiche della cittadinanza attiva richiedono competenze diversificate, che \u00e8 difficile trovare tutte in una sola persona. E quelle persone, semplicemente, <strong>non si trovano</strong>. Non perch\u00e9 si nascondano: perch\u00e9 non c\u2019\u00e8 nessun posto dove guardare.</p>

<h2>Ogni volta si riparte da zero</h2>

<p>La conseguenza \u00e8 uno spreco continuo.</p>

<p>Un gruppo apre una battaglia sulla sanit\u00e0 in una provincia, e non sa che a quaranta chilometri un altro gruppo ha gi\u00e0 raccolto i dati, gi\u00e0 scritto l\u2019esposto, gi\u00e0 incassato il rifiuto e imparato dove stava l\u2019errore. Un comitato si costituisce contro una delibera, e ignora che nella stessa regione c\u2019\u00e8 chi quella delibera l\u2019ha gi\u00e0 impugnata.</p>

<p>Nel frattempo, chi ha il potere di decidere non ha questo problema. Ha uffici, consulenti, banche dati, continuit\u00e0. <strong>La disparit\u00e0 non \u00e8 solo di forza: \u00e8 di organizzazione.</strong></p>

<h2>Cosa abbiamo costruito</h2>

<p>Partecipazione Attiva ha una mappa.</p>

<p>Ognuno scrive dove si trova, quali temi gli stanno a cuore e quali competenze pu\u00f2 mettere a disposizione. Poi si cerca \u2014 per tema, per competenza, per luogo \u2014 e si trova chi si sta battendo per le stesse cose l\u00ec vicino. Cittadini singoli e associazioni, in Italia e nel mondo.</p>

<p><strong>Non \u00e8 un tesseramento.</strong> Entrare nella mappa non \u00e8 iscriversi a Partecipazione Attiva: non c\u2019\u00e8 quota, non c\u2019\u00e8 adesione, non si rinuncia alla propria sigla n\u00e9 alla propria autonomia. La mappa l\u2019abbiamo costruita noi e ne paghiamo i costi, ma \u00e8 uno spazio comune.</p>

<p>Chi entra resta esattamente quello che era. In pi\u00f9, <strong>diventa trovabile</strong>.</p>

<h2>Le persone, non i dati</h2>

<p>Una precisazione che conta, perch\u00e9 sappiamo che \u00e8 la prima obiezione.</p>

<p>Sulla mappa compaiono solo il nome con l\u2019iniziale del cognome \u2014 o il nome dell\u2019associazione \u2014 il comune, i temi, le competenze e la descrizione che ciascuno scrive di s\u00e9. <strong>L\u2019email non \u00e8 mai pubblica.</strong> Il punto sulla mappa \u00e8 il centro del comune, mai l\u2019indirizzo di casa: <strong>non usiamo il GPS</strong>.</p>

<p>Se qualcuno vuole mettersi in contatto, manda un messaggio. Chi lo riceve legge, valuta e decide: solo se accetta, i due indirizzi vengono scambiati. Chi non risponde non subisce nulla, e chi ha scritto non avr\u00e0 mai il suo recapito.</p>

<p>I dati stanno su server europei e <strong>si cancellano con un click</strong>, in qualsiasi momento.</p>

<h2>Perch\u00e9 lo facciamo</h2>

<p>Il nostro Manifesto, nel 2022, si proponeva di:</p>

<blockquote style="border-left:4px solid #e8900a;padding:18px 24px;margin:32px 0;background:#fff8ee;border-radius:0 12px 12px 0;font-family:merriweather,serif;font-style:italic;color:#5a3200;font-size:1.08em;line-height:1.8">
\u201cporre in atto azioni pubbliche di superamento dell\u2019individualismo, favorendo una cooperazione che permetta di creare quella massa critica e rete di condivisione, per consentire al gruppo di ottenere risultati solidali.\u201d
</blockquote>

<p>La Mappa \u00e8 quella frase resa strumento.</p>

<p>Serve massa critica: con venti nomi resta un esercizio. Con duecento, cambia il modo in cui ci si muove. Ma il primo passo non lo pu\u00f2 fare un movimento \u2014 lo fanno le persone, una alla volta.</p>

<div class="pa-cta">
<p>Entra nella Mappa. Cerca chi ti somiglia. Cominciamo a contarci.</p>
<a href="mappa.html">\U0001F5FA\ufe0f Vai alla Mappa</a>
</div>
'''

BODY_STABILICUM_LUGLIO = '''
<style>
.pa-lead{font-size:1.12em!important;color:#8a4e00!important;font-weight:600}
.pa-cta{background:#fff8ee;border:2px solid #ffd580;border-radius:16px;padding:28px 32px;margin:36px 0;text-align:center}
.pa-cta p{font-family:merriweather,serif;color:#333;font-size:1.1em;font-weight:700;margin-bottom:16px}
.pa-cta a{display:inline-block;background:#e8900a;color:#fff;text-decoration:none;padding:14px 32px;border-radius:50px;font-family:montserrat,sans-serif;font-weight:700;font-size:.95em}
</style>

<p class="pa-lead">Da marted&igrave; 14 luglio l&rsquo;Aula della Camera comincia a votare la nuova legge elettorale. La chiamano Stabilicum. Le opposizioni la chiamano Melonellum. Il nome cambia poco: quello che conta &egrave; cosa fa.</p>

<p>E in questi giorni tutto ruota attorno a una parola: preferenze.</p>

<p>Il racconto che arriva ai cittadini &egrave; semplice. Fratelli d&rsquo;Italia vuole restituirti il potere di scegliere il tuo deputato. Forza Italia e la Lega non vogliono. &Egrave; una battaglia per la democrazia.</p>

<p><strong>Guardiamo i fatti, non la maglietta.</strong></p>

<h2>La preferenza che non &egrave; una preferenza</h2>

<p>L&rsquo;emendamento presentato da Fratelli d&rsquo;Italia, Noi Moderati e UDC prevede un capolista bloccato &mdash; cio&egrave; scelto dal partito &mdash; e sotto di lui sei candidati, tra cui potrai indicare fino a tre preferenze.</p>

<p>Sembra un passo avanti. Ma leggiamo cosa succede davvero quando si contano i voti.</p>

<p>Chi tra i candidati non bloccati prende pi&ugrave; preferenze pu&ograve; essere eletto solo se in quel collegio il partito elegge pi&ugrave; di un candidato. Se ne elegge uno solo, va al capolista &mdash; a prescindere da quante preferenze abbiano preso gli altri.</p>

<p>Ora, la domanda concreta: in quanti collegi un partito elegge pi&ugrave; di un deputato?</p>

<p>In pochi. Nella grande maggioranza dei collegi plurinominali, un partito di medie dimensioni elegge un solo candidato. E quel candidato &egrave; il capolista.</p>

<p>Il che significa: <strong>nella maggior parte dei casi, la tua preferenza non sposta nulla</strong>. Il deputato lo ha gi&agrave; scelto la segreteria. Tu puoi tracciare tutte le X che vuoi.</p>

<p>Non &egrave; una preferenza. &Egrave; l&rsquo;ombra di una preferenza.</p>

<h2>Perch&eacute; litigano davvero</h2>

<p>Se il litigio non &egrave; sul tuo diritto di scegliere, su cosa &egrave;?</p>

<p><strong>Sui soldi e sui seggi.</strong></p>

<p>Lega e Forza Italia sono contrarie per una ragione che nessuno dei loro dirigenti dir&agrave; mai a un microfono: con i sondaggi attuali, i loro candidati sanno gi&agrave; di non avere concrete possibilit&agrave; di essere eletti. E fare campagna con le preferenze &egrave; costoso: si parla di decine di migliaia di euro, e per i candidati pi&ugrave; ricchi si arriva a centinaia. Chi non pu&ograve; spendere, non compete.</p>

<p>Forza Italia, ufficialmente, adduce un&rsquo;altra ragione: il rischio di infiltrazioni della criminalit&agrave; organizzata in alcune aree. &Egrave; un argomento serio, in astratto. Ma nessuno spiega perch&eacute; lo stesso rischio non valga per le elezioni regionali ed europee, dove le preferenze ci sono da sempre.</p>

<p>Fratelli d&rsquo;Italia le vuole per ragioni altrettanto poco nobili: Meloni le ha promesse per anni, e ora che la legge la scrive lei non pu&ograve; fare marcia indietro senza perdere la faccia &mdash; anche perch&eacute; Vannacci la incalza da destra.</p>

<p>E c&rsquo;&egrave; il ricatto, che &egrave; la parte pi&ugrave; istruttiva. Se l&rsquo;emendamento sulle preferenze cade, Fratelli d&rsquo;Italia minaccia di tornare al testo base: premio di maggioranza alla lista pi&ugrave; votata, non alla coalizione. Tradotto: FdI prende tutto, e a Lega e Forza Italia non resta un seggio blindato.</p>

<p><strong>Il cittadino, in questo calcolo, non compare mai.</strong></p>

<h2>Il motivo tecnico che non ti dicono</h2>

<p>C&rsquo;&egrave; un&rsquo;ultima ragione per cui le preferenze fanno comodo, e riguarda un&rsquo;aula diversa da quella di Montecitorio.</p>

<p>Un sistema interamente a liste bloccate rischia grosso davanti alla Corte Costituzionale. Non &egrave; una previsione: &egrave; gi&agrave; successo. L&rsquo;Italicum &mdash; la legge di Renzi, che a questa somigliava &mdash; fu bocciato dalla Consulta nel 2017 proprio su quel terreno.</p>

<p>Inserire un simulacro di preferenza serve anche a questo: blindare la legge da un possibile siluro della Corte.</p>

<p>Il che spiega perch&eacute; la preferenza proposta sia congegnata come &egrave;: <strong>abbastanza da poter dire che c&rsquo;&egrave;, troppo poco perch&eacute; cambi qualcosa</strong>.</p>

<h2>Cosa succede in Aula</h2>

<p>Da marted&igrave; la Camera vota. Si comincia con le pregiudiziali di costituzionalit&agrave; sollevate dalle opposizioni.</p>

<p>Poi, quasi certamente, si passa allo scrutinio segreto &mdash; il regolamento lo prevede per le materie elettorali. &Egrave; il momento in cui i deputati votano senza che il partito sappia come. E in cui si scopre quanti, dentro la maggioranza, la pensano diversamente da chi li comanda.</p>

<p>Anche dentro Fratelli d&rsquo;Italia, viene riferito, non tutti sono d&rsquo;accordo.</p>

<p>Alle 18, davanti a Montecitorio, ci sar&agrave; la piazza convocata da Riccardo Magi &mdash; la &ldquo;Notte della democrazia&rdquo; &mdash; con Conte, Fratoianni e Bonelli.</p>

<h2>Le cose serie di cui nessuno parla</h2>

<p>Mentre l&rsquo;attenzione &egrave; tutta sulle preferenze, nella stessa legge passano cose che riguardano milioni di persone.</p>

<p><strong>Il voto ai fuorisede.</strong> Un emendamento della maggioranza permetterebbe a chi studia o lavora lontano dalla residenza di votare dov&rsquo;&egrave;. Riguarderebbe circa cinque milioni di cittadini, che oggi per votare devono pagarsi un viaggio. &Egrave; una misura giusta, chiesta da anni. Ma il Partito Democratico sostiene che cos&igrave; com&rsquo;&egrave; scritta sia troppo rigida &mdash; un bluff. Su questo varrebbe la pena litigare.</p>

<p><strong>La circoscrizione Estero</strong>, ridotta da quattro a due ripartizioni per la Camera e a una sola per il Senato. Milioni di italiani residenti all&rsquo;estero, rappresentati da un numero di seggi invariato ma su aree geografiche enormemente pi&ugrave; grandi.</p>

<p><strong>Le firme per presentarsi.</strong> Un emendamento esenta dalla raccolta firme i partiti che a dicembre 2025 avevano un gruppo parlamentare. Chi &egrave; nato dopo &mdash; o chi viene da fuori &mdash; le firme le raccoglie. Chi c&rsquo;era gi&agrave;, no.</p>

<p>Quest&rsquo;ultima merita una riflessione. Una legge elettorale scritta da chi &egrave; in Parlamento, che rende pi&ugrave; facile restarci a chi c&rsquo;&egrave; gi&agrave; e pi&ugrave; difficile entrare a chi non c&rsquo;&egrave;.</p>

<h2>La domanda che resta</h2>

<p>Qualunque sia l&rsquo;esito del voto di questa settimana &mdash; preferenze s&igrave;, preferenze no, preferenze finte &mdash; una cosa non cambia.</p>

<p>Chi decide i candidati? Le segreterie.</p>

<p>Chi decide chi guida il Paese? Un premio di maggioranza che scatta al 42%, assegnando 70 seggi alla Camera e 35 al Senato a chi arriva primo.</p>

<p>E il cittadino? Il cittadino sceglie tra liste che qualcun altro ha compilato, per un premier che qualcun altro ha indicato, con una preferenza che nella maggior parte dei casi non sposter&agrave; nulla.</p>

<p>Poi torna a casa, e per cinque anni non gli viene chiesto pi&ugrave; niente.</p>

<p><strong>Questo &egrave; il punto che nessuno, in questa settimana di grande agitazione, sta discutendo. E non &egrave; una questione di destra o di sinistra: &egrave; una questione di chi tiene la penna.</strong></p>

<p style="font-style:italic;font-size:.88em;color:#888;margin-top:28px">Partecipazione Attiva segue l&rsquo;iter dello Stabilicum e sostiene il ricorso pendente in Cassazione contro il Rosatellum, la cui udienza &egrave; fissata per il 29 ottobre.</p>

<div class="pa-cta">
<p>Ti occupi di questo tema? Mettiti sulla mappa e trova chi se ne occupa vicino a te.</p>
<a href="mappa.html">\U0001F5FA\ufe0f Vai alla Mappa</a>
</div>
'''

BODY_NOTTE_DEMOCRAZIA = '''
<style>
.pa-lead{font-size:1.12em!important;color:#8a4e00!important;font-weight:600}
.pa-fig{margin:32px 0}
.pa-fig img{width:100%;border-radius:14px;box-shadow:0 6px 20px rgba(0,0,0,.12)}
.pa-fig figcaption{font-family:montserrat,sans-serif;font-size:.82em;color:#9c5b00;margin-top:10px;text-align:center;font-style:italic}
.pa-event{background:#8a4e00;color:#fff;border-radius:16px;padding:26px 30px;margin:32px 0;text-align:center}
.pa-event .tit{font-family:montserrat,sans-serif;font-weight:900;letter-spacing:1px;font-size:1.15em;margin-bottom:12px}
.pa-event p{color:#fff!important;margin:6px 0}
.pa-cta{background:#fff8ee;border:2px solid #ffd580;border-radius:16px;padding:28px 32px;margin:36px 0;text-align:center}
.pa-cta p{font-family:merriweather,serif;color:#333;font-size:1.1em;font-weight:700;margin-bottom:16px}
.pa-cta a{display:inline-block;background:#e8900a;color:#fff;text-decoration:none;padding:14px 32px;border-radius:50px;font-family:montserrat,sans-serif;font-weight:700;font-size:.95em}
</style>

<p class="pa-lead">Oggi, marted&igrave; 14 luglio, la Camera comincia a votare la nuova legge elettorale. Il centrodestra la chiama Stabilicum. Le opposizioni la chiamano Melonellum.</p>

<p>Stasera Partecipazione Attiva sar&agrave; in piazza Montecitorio, insieme ad altre associazioni e movimenti, per la Notte della Democrazia.</p>

<p>Dalle 18, punto stampa. A seguire, veglia con talk, musica e flash mob.</p>

<p>Il nostro portavoce <strong>Luigi Spanu</strong> sar&agrave; presente con i volantini del movimento, per riprendere la manifestazione e rilasciare interviste.</p>

<h2>Perch&eacute; ci siamo</h2>

<p>Non &egrave; una questione di schieramento. &Egrave; una questione di chi tiene la penna.</p>

<p>Questa mattina abbiamo pubblicato l&rsquo;analisi di cosa la Camera sta davvero votando: una preferenza che, nella maggior parte dei collegi, non sposterebbe nulla, perch&eacute; il seggio andrebbe comunque al capolista scelto dalla segreteria.</p>

<p><a href="preferenze-stabilicum-luglio2026.html">La preferenza che non ti fa scegliere</a></p>

<p>Ma il problema non &egrave; solo quello.</p>

<h3>Un premierato mascherato da legge elettorale</h3>

<p>Le liste dovranno indicare, al momento del deposito del contrassegno, il nome del candidato Presidente del Consiglio. <strong>Non &egrave; una legge elettorale: &egrave; una modifica di fatto della forma di governo</strong>, ottenuta senza passare da una riforma costituzionale &mdash; e quindi senza il referendum che la Costituzione prevede.</p>

<p>L&rsquo;articolo 92 della Costituzione affida al Presidente della Repubblica la nomina del Presidente del Consiglio. Indicare il premier sulla scheda comprime quella prerogativa senza dirlo apertamente.</p>

<h3>Liste bloccate</h3>

<p>Il cittadino vota un simbolo. I nomi li hanno gi&agrave; scelti le segreterie.</p>

<p>&Egrave; esattamente il meccanismo che la Corte Costituzionale, con la sentenza 1/2014, dichiar&ograve; illegittimo per il Porcellum:</p>

<blockquote style="border-left:4px solid #e8900a;padding:18px 24px;margin:32px 0;background:#fff8ee;border-radius:0 12px 12px 0;font-family:merriweather,serif;font-style:italic;color:#5a3200;font-size:1.08em;line-height:1.8">
&ldquo;coartano la libert&agrave; di scelta degli elettori nell&rsquo;elezione dei propri rappresentanti in Parlamento&rdquo; &mdash; Corte Costituzionale, sentenza n. 1/2014
</blockquote>

<p><strong>Dodici anni dopo, siamo ancora qui.</strong></p>

<h3>Chi c&rsquo;&egrave; gi&agrave; dentro, ci resta pi&ugrave; facilmente</h3>

<p>Un emendamento esenta dalla raccolta firme i partiti che a dicembre 2025 avevano un gruppo parlamentare. Chi &egrave; nato dopo, o viene da fuori, le firme le raccoglie &mdash; e in Italia il numero richiesto &egrave; tra i pi&ugrave; alti d&rsquo;Europa.</p>

<p>Una legge elettorale scritta da chi &egrave; in Parlamento, che rende pi&ugrave; facile restarci a chi c&rsquo;&egrave; gi&agrave;.</p>

<h3>Il voto ai fuorisede, all&rsquo;ultimo momento</h3>

<p>Circa cinque milioni di elettori vivono lontano dalla residenza per studio, lavoro o cura. Per votare devono pagarsi un viaggio: <strong>il 5% degli elettori affronta oltre quattro ore tra andata e ritorno</strong>. L&rsquo;Italia &egrave; l&rsquo;unico grande Paese europeo senza una legge stabile sul voto fuorisede.</p>

<p>L&rsquo;emendamento della maggioranza &egrave; arrivato all&rsquo;ultimo momento, dopo essere stato assente dalle versioni precedenti. Ed &egrave; scritto in modo cos&igrave; rigido &mdash; dicono le opposizioni &mdash; da rischiare di non funzionare davvero.</p>

<p>Su questo varrebbe la pena litigare. Invece si litiga su una preferenza che non fa scegliere.</p>

<h2>Non basta dire no</h2>

<p>E qui va detta una cosa che non far&agrave; piacere a nessuno.</p>

<p><strong>Respingere il Melonellum non basta.</strong> Perch&eacute; il Rosatellum oggi in vigore &egrave; altrettanto incostituzionale, e altrettanto pericoloso: le liste bloccate ci sono gi&agrave;, il voto congiunto pure, le pluricandidature anche.</p>

<p>Se domani il Melonellum cadesse, torneremmo a votare con una legge che nega esattamente le stesse cose.</p>

<p>Per questo, insieme a Lista Civica Italiana, chiediamo alle forze del cosiddetto campo largo di rendere pubblica adesso la legge elettorale che si impegnano ad approvare in caso di vittoria.</p>

<p><strong>Non dopo il voto. Adesso.</strong></p>

<p>Perch&eacute; una legge elettorale rispettosa della Costituzione &mdash; semplice, breve, comprensibile &mdash; &egrave; il presupposto di tutto il resto. E chi chiede il voto dei cittadini contro una legge che toglie loro la scelta, <strong>ha il dovere di dire con quale legge intende restituirgliela</strong>.</p>

<div class="pa-fig">
<img src="images/volantino-melonellum.webp" alt="Volantino di Partecipazione Attiva e Lista Civica Italiana contro il Melonellum">
<figcaption>Il volantino di Partecipazione Attiva e Lista Civica Italiana, distribuito stasera in piazza.</figcaption>
</div>

<h2>Se non puoi venire a Roma</h2>

<p>C&rsquo;&egrave; comunque una cosa che puoi fare, e servono lo SPID e cinque minuti.</p>

<p>Tre proposte di legge di iniziativa popolare, depositate dall&rsquo;associazione Voto LibEguale, chiedono esattamente ci&ograve; che manca: preferenze vere su nomi prestampati, primarie per tutti i candidati, abolizione delle pluricandidature e del voto congiunto.</p>

<p>L&rsquo;articolo 74 del Regolamento del Senato obbliga a calendarizzarle entro tre mesi. Se le firme arrivassero adesso, l&rsquo;esame cadrebbe mentre lo Stabilicum &egrave; al Senato.</p>

<p>Si firma su <a href="https://votolibeguale.it" target="_blank" rel="noopener">votolibeguale.it</a></p>

<div class="pa-event">
<div class="tit">\u270a NOTTE DELLA DEMOCRAZIA</div>
<p><strong>Marted&igrave; 14 luglio, dalle 18.00</strong></p>
<p>Roma, Piazza Montecitorio</p>
<p>Punto stampa, veglia, talk, musica, flash mob</p>
</div>

<div class="pa-cta">
<p>Ti occupi di questo tema? Mettiti sulla mappa e trova chi se ne occupa vicino a te.</p>
<a href="mappa.html">\U0001F5FA\ufe0f Vai alla Mappa</a>
</div>
'''

ART_NOTTE_DEMOCRAZIA = {
  'slug'         : 'notte-democrazia-montecitorio.html',
  'autore'       : 'pa',
  'data_iso'     : '2026-07-14',
  'data_human'   : '14 luglio 2026',
  'data_badge'   : '14 LUGLIO 2026',
  'lettura_min'  : 4,
  'categoria_hero': '\u270a Mobilitazione',
  'og_image'     : 'images/notte-democrazia.webp',
  'h1'           : 'Stasera siamo a Montecitorio',
  'sottotitolo'  : 'Mentre l\u2019Aula vota lo Stabilicum, Partecipazione Attiva \u00e8 in piazza con la Notte della Democrazia. Il nostro portavoce Luigi Spanu sar\u00e0 presente dalle 18.',
  'meta_desc'    : 'Partecipazione Attiva in piazza Montecitorio per la Notte della Democrazia. No alle liste bloccate, no al premierato mascherato da legge elettorale.',
  'card_cat'     : 'MOBILITAZIONE',
  'card_title'   : 'Stasera siamo a Montecitorio',
  'card_desc'    : 'Mentre l\u2019Aula vota lo Stabilicum, PA \u00e8 in piazza per la Notte della Democrazia. Il portavoce Luigi Spanu presente dalle 18.',
  'ticker_emoji' : '\u270a',
  'ticker_tema'  : 'NOTTE DELLA DEMOCRAZIA',
  'ticker_testo' : 'PA in piazza Montecitorio stasera dalle 18 contro lo Stabilicum \u2014 con il portavoce Luigi Spanu',
  'body'         : BODY_NOTTE_DEMOCRAZIA,
}
# ===========================================================================

BODY_STABILICUM_PREFERENZE = '''
<article class="article-wrap">

<div class="box-info" style="border-left-color:#8a4e00">
<strong>In breve</strong>
La Camera boccia a scrutinio segreto l&rsquo;emendamento della maggioranza sulle preferenze: 188 contrari, 187 favorevoli, manca un solo voto. Il governo resta in carica; il testo torna ora al Senato, dove il voto sar&agrave; palese.
</div>

<p>Ieri pomeriggio, marted&igrave; 14 luglio 2026, la Camera ha bocciato a scrutinio segreto l&rsquo;emendamento della maggioranza sulle preferenze nella nuova legge elettorale. &Egrave; mancato un solo voto: 188 contrari, 187 favorevoli.</p>

<p>L&rsquo;emendamento &mdash; a prima firma Fratelli d&rsquo;Italia, Noi Moderati e UDC &mdash; introduceva un sistema misto con capolista bloccato e fino a tre preferenze in una scheda con sette nomi. Nelle ore precedenti Giorgia Meloni si era esposta in prima persona: aveva chiamato i ministri in aula e, con un post sui social, aveva contestato la richiesta di voto segreto avanzata dalle opposizioni, invitando i parlamentari a &laquo;metterci la faccia&raquo;. Governo e relatori avevano dato parere favorevole. A far mancare i numeri sono stati, secondo i primi conti, una trentina di franchi tiratori interni alla stessa maggioranza.</p>

<p>Subito dopo il voto, i leader delle opposizioni &mdash; in aula e al presidio davanti a Montecitorio &mdash; hanno chiesto compatti le dimissioni della premier. Giuseppe Conte ha invitato Meloni ad aprire la crisi di governo; Elly Schlein ha parlato di un voto contro l&rsquo;arroganza dell&rsquo;esecutivo e di un&rsquo;occasione per dare al Paese un governo capace di affrontare i problemi reali; Nicola Fratoianni ha letto il risultato come una sfiducia sostanziale. Dall&rsquo;aula si sono levati i cori &laquo;elezioni&raquo; e &laquo;dimissioni&raquo;.</p>

<p>Va detto con precisione, per non alimentare equivoci: la bocciatura di un singolo emendamento non fa cadere il governo, che resta in carica. La maggioranza ha gi&agrave; annunciato di voler proseguire &mdash; il ministro Antonio Tajani ha derubricato l&rsquo;accaduto a &laquo;incidente di percorso&raquo; &mdash; e il presidente del Senato Ignazio La Russa ha ricordato che a Palazzo Madama, dove sul punto non &egrave; previsto il voto segreto, il testo potr&agrave; essere corretto. La premier, a caldo, ha commentato con amarezza: &laquo;ha vinto di nuovo la palude&raquo;.</p>

<h2>Partecipazione Attiva al presidio</h2>

<p>All&rsquo;iniziativa era presente anche Partecipazione Attiva, in qualit&agrave; di comitato referendario &mdash; lo stesso che nel 2024 aveva promosso il referendum su questi temi. Il nostro portavoce ha ribadito la posizione del movimento: la nuova legge elettorale, cos&igrave; com&rsquo;&egrave; impostata, rischia di maturare l&rsquo;ennesimo atto di incostituzionalit&agrave;, costringendo poi a inseguirla con iniziative giudiziarie. Il nodo resta quello di sempre, la libert&agrave; di scelta dell&rsquo;elettore: liste e capilista bloccati svuotano il voto, e l&rsquo;emendamento sulle preferenze, per come era congegnato, non lo restituiva davvero ai cittadini.</p>

<div style="max-width:360px;margin:32px auto;aspect-ratio:9/16;border-radius:14px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,.15)">
<iframe src="https://www.youtube.com/embed/Z29yksFdA4k" title="Partecipazione Attiva al presidio davanti a Montecitorio" width="100%" height="100%" style="display:block;border:0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>
</div>

<h2>Cosa succede ora</h2>

<p>L&rsquo;esame della legge &mdash; il cosiddetto &laquo;Stabilicum&raquo;, sistema proporzionale con premio di maggioranza per chi supera maggiormente il 42% dei voti &mdash; prosegue. Con la bocciatura delle preferenze restano le liste bloccate, e la partita si sposta al Senato, dove il voto palese cambia gli equilibri. Partecipazione Attiva continuer&agrave; a seguire il percorso del provvedimento e a vigilare sui profili di costituzionalit&agrave;, come fa dalla stagione referendaria del 2024.</p>

</article>
'''

ART_STABILICUM_PREFERENZE_BOCCIATE = {
  'slug'         : 'stabilicum-preferenze-bocciate-14lug2026.html',
  'autore'       : 'pa',
  'data_iso'     : '2026-07-15',
  'data_human'   : '15 luglio 2026',
  'data_badge'   : '15 LUGLIO 2026',
  'lettura_min'  : 3,
  'categoria_hero': '⚖️ Riforma elettorale',
  'og_image'     : 'images/stabilicum-preferenze-bocciate-14lug2026.jpg',
  'h1'           : 'Legge elettorale, la maggioranza battuta alla Camera sulle preferenze',
  'sottotitolo'  : 'A scrutinio segreto, la Camera boccia per un solo voto l’emendamento sulle preferenze. Le opposizioni chiedono le dimissioni della premier, la maggioranza resta in carica.',
  'meta_desc'    : 'La Camera boccia a scrutinio segreto l’emendamento sulle preferenze nella legge elettorale: 188 contrari, 187 favorevoli. Il resoconto e la posizione di Partecipazione Attiva al presidio di Montecitorio.',
  'card_cat'     : 'RIFORMA ELETTORALE',
  'card_title'   : 'La maggioranza battuta alla Camera sulle preferenze',
  'card_desc'    : 'Bocciato per un solo voto l’emendamento sulle preferenze. PA al presidio di Montecitorio: la nuova legge rischia un altro atto di incostituzionalità.',
  'ticker_emoji' : '⚖️',
  'ticker_tema'  : 'STABILICUM',
  'ticker_testo' : 'la Camera boccia per un voto l’emendamento sulle preferenze, la maggioranza resta in carica',
  'body'         : BODY_STABILICUM_PREFERENZE,
}
# ===========================================================================

BODY_STABILICUM_NOTA_SPANU = '''
<article class="article-wrap">

<p>Ieri, 16 luglio 2026, la Camera ha approvato la nuova legge elettorale — lo Stabilicum — con 217 voti favorevoli, 152 contrari e 2 astenuti, a scrutinio segreto. Il testo passa ora al Senato. Come portavoce nazionale di Partecipazione Attiva voglio dire con chiarezza cosa pensiamo, e perché la questione riguarda ogni cittadino, di qualsiasi orientamento.</p>

<p>Partiamo da un punto che teniamo a non lasciare equivoco: <strong>non siamo contrari alla stabilità di governo</strong>. È un obiettivo legittimo, e chi lo persegue non fa nulla di sbagliato. Il nostro problema è un altro, ed è di metodo prima ancora che di merito.</p>

<p>Una legge elettorale non è una legge come le altre. È la regola con cui i cittadini esercitano la sovranità che la Costituzione affida loro. Per questo non può essere scritta da una sola parte, a proprio vantaggio. E colpisce che l'approvazione sia arrivata a scrutinio segreto, due giorni dopo che la stessa maggioranza, sempre nel segreto dell'urna, aveva affossato per un solo voto le preferenze, con oltre trenta franchi tiratori nelle proprie file. Quando una maggioranza teme i propri stessi voti, il segnale è chiaro: si è scelto di sottrarre ai cittadini la possibilità di scegliere i propri rappresentanti.</p>

<p>Perché è di questo che si tratta. Con le liste bloccate previste dallo Stabilicum, a scegliere gli eletti non sono gli elettori ma le segreterie dei partiti. Non è un dettaglio tecnico: è il cuore del rapporto tra chi vota e chi viene votato.</p>

<p>Ci sono poi altri aspetti su cui vigileremo:</p>

<ul style="font-family:merriweather,serif;font-size:1em;line-height:1.85;color:#333;margin:0 0 24px;padding-left:22px"><li style="margin-bottom:14px">Il <strong>premio di governabilità</strong> che scatta al 42% dei voti — 70 seggi in più alla Camera, 35 al Senato — riporta il sistema verso quei premi che la Corte costituzionale ha già bocciato in passato, con il Porcellum nel 2014 e con parti dell'Italicum nel 2017. La questione di costituzionalità è aperta, e non a caso è già stato annunciato un fronte di ricorsi.</li><li style="margin-bottom:14px">L'<strong>esenzione dalla raccolta firme</strong> riservata a chi aveva un gruppo parlamentare entro il 31 dicembre 2025 favorisce chi è già dentro e alza il muro davanti ai movimenti più recenti. È l'opposto di regole uguali per tutti.</li></ul>

<p>Il percorso non è concluso. Il testo va al Senato, dove può ancora cambiare, e dove la partita sulle preferenze può riaprirsi — questa volta, ci auguriamo, alla luce del sole. Chiediamo che questo passaggio avvenga con il confronto che finora è mancato, e nel rispetto dei tempi: anche dal Quirinale è arrivato il richiamo a non toccare la legge elettorale troppo a ridosso del voto.</p>

<p>Partecipazione Attiva continuerà a seguire l'iter passo dopo passo e a informare i cittadini, come ha fatto dal primo giorno. Su come si vota non esistono spettatori. Riguarda tutti noi.</p>

<p style="font-style:italic;color:#8a4e00;margin-top:32px">Luigi Spanu<br>Portavoce nazionale — Partecipazione Attiva</p>

</article>
'''

ART_STABILICUM_NOTA_SPANU = {
  'slug'         : 'stabilicum-nota-spanu-17lug2026.html',
  'autore'       : 'spanu',
  'data_iso'     : '2026-07-17',
  'data_human'   : '17 luglio 2026',
  'data_badge'   : '17 LUGLIO 2026',
  'lettura_min'  : 3,
  'categoria_hero': '⚖️ Riforma elettorale',
  'og_image'     : 'images/spanu-audizione-stabilicum.webp',
  'h1'           : 'Stabilicum, la nota del portavoce Luigi Spanu: «Le regole del voto non le scrive una parte sola»',
  'sottotitolo'  : 'Dopo l’approvazione a scrutinio segreto alla Camera, il portavoce di Partecipazione Attiva: liste bloccate e premio di maggioranza restano il nodo. Ora il testo passa al Senato.',
  'meta_desc'    : 'La nota del portavoce nazionale Luigi Spanu dopo il sì della Camera allo Stabilicum: una legge elettorale non può essere scritta da una sola parte. Il testo passa ora al Senato.',
  'card_cat'     : 'RIFORMA ELETTORALE',
  'card_title'   : 'La nota del portavoce Luigi Spanu sullo Stabilicum',
  'card_desc'    : 'Dopo il sì della Camera a scrutinio segreto: liste bloccate e premio di maggioranza restano il nodo. Il testo passa al Senato.',
  'ticker_emoji' : '⚖️',
  'ticker_tema'  : 'STABILICUM',
  'ticker_testo' : 'la Camera approva lo Stabilicum a scrutinio segreto, la nota del portavoce Luigi Spanu — ora il testo va al Senato',
  'body'         : BODY_STABILICUM_NOTA_SPANU,
}
# ===========================================================================

BODY_STABILICUM_CREPE = '''
<article class="article-wrap">

<p>Immagina di votare una lista, e che il tuo voto — invece di eleggere chi hai scelto — finisca per rafforzare qualcun altro. Oppure di non poter scegliere nessun nome, perché gli eletti li decide la segreteria del partito. Non è fantapolitica: sono due dei nodi della nuova legge elettorale che la Camera ha appena approvato, lo Stabilicum.</p>

<p>Il testo ora passa al Senato. Ma se il Senato lo confermerà così com'è, la partita si sposterà davanti alla Corte costituzionale. E lì, secondo chi conosce quel terreno, la legge rischia grosso.</p>

<p>A metterlo nero su bianco è l'avvocato Beppe Sarno, in <a href="https://www.criticasociale.net/articolo-primo-piano-it.php?id=57" target="_blank" rel="noopener nofollow">un'analisi su Critica Sociale</a>: sette punti di sospetta incostituzionalità. Sarno è tra i giuristi che hanno affiancato Felice Besostri nelle battaglie che hanno già portato due leggi elettorali davanti alla Consulta — e le hanno viste cadere. Vale la pena tradurre il suo ragionamento in parole semplici, perché parla del peso del voto di ciascuno di noi.</p>

<h2>La Corte queste cose le ha già bocciate</h2>
<p>Non partiamo da zero. Nel 2014, con la sentenza n. 1, la Corte costituzionale bocciò il "Porcellum": premio di maggioranza troppo grande e senza soglia minima, e liste bloccate che nascondevano i candidati agli elettori. Nel 2017, con la sentenza n. 35, dichiarò incostituzionali pezzi dell'"Italicum", tra cui il ballottaggio e il trucco per cui un capolista poteva candidarsi ovunque e poi scegliere dove farsi eleggere.</p>
<p>Lo Stabilicum torna a muoversi sugli stessi terreni. Ecco i più fragili.</p>

<h2>Il premio può essere troppo generoso</h2>
<p>Chi arriva al 42% dei voti riceve 70 deputati e 35 senatori in più. Sempre gli stessi, sia che tu raggiunga appena il 42%, sia che tu sia già vicino alla maggioranza da solo. È un premio "fisso", non tagliato su misura dei seggi che servono davvero a governare. Nel primo caso può non bastare; nel secondo diventa un regalo che gonfia una maggioranza già forte. È qui, nella sproporzione tra mezzo e fine, la crepa più profonda.</p>
<p>Il tetto di 220 deputati e 113 senatori limita i danni, ma non li chiude: se i seggi delle circoscrizioni speciali si sommassero al limite, la maggioranza reale supererebbe quella dichiarata. E c'è un dettaglio non da poco: il premio va anche a una coalizione, che può nascere per incassarlo e sciogliersi il giorno dopo il voto. Si sacrifica la rappresentanza in nome della stabilità, senza garanzia che quella stabilità duri.</p>

<h2>Il tuo voto può andare a chi non hai scelto</h2>
<p>È il punto più tecnico, ed è quello a cui Besostri ha dedicato la vita. La legge somma soglia su soglia: per le liste, per le coalizioni, per il premio. Il rischio concreto è che il voto a una piccola lista sotto soglia non elegga nessuno di quella lista — ma finisca comunque per contribuire al premio della coalizione. In parole povere: il tuo voto non porta in Parlamento chi volevi, però aiuta chi non volevi. Un voto dovrebbe avere un effetto chiaro e prevedibile, non essere spostato per automatismo verso qualcun altro.</p>

<h2>Gli eletti li scegli tu, o il partito?</h2>
<p>Con le liste bloccate, la risposta è: il partito. È il cuore della <a href="stabilicum-nota-spanu-17lug2026.html">nota del nostro portavoce Luigi Spanu</a>. La Corte non ha vietato ogni lista bloccata, ma nel 2014 ha bocciato quelle così lunghe da impedire ai cittadini di sapere chi stanno votando. Il premio peggiora tutto: anche i seggi in più vengono assegnati nell'ordine deciso dagli apparati, e a volte non sai nemmeno in quale territorio scatterà l'elezione.</p>

<h2>Il premier stampato sulla scheda</h2>
<p>Lo Stabilicum mette sulla scheda il nome del candidato premier. In sé non è vietato. Ma l'Italia è una Repubblica parlamentare: il Presidente del Consiglio lo nomina il Capo dello Stato e deve avere la fiducia delle Camere. La norma regge solo se quell'indicazione ha un valore politico, non giuridico. Se invece facesse credere di eleggere direttamente il premier, si cambierebbe di fatto la forma di governo con una legge ordinaria — scavalcando la revisione costituzionale che servirebbe.</p>

<h2>E chi vuole entrare in campo?</h2>
<p>Resta il nodo già segnalato: l'esenzione dalla raccolta firme riservata a chi aveva già un gruppo in Parlamento. Una legge può aiutare chi c'è, ma non può blindare il sistema esistente chiudendo la porta ai movimenti nuovi. Firme numerose, tempi stretti, niente raccolta digitale ed esenzioni "per pochi": messe insieme, toccano princìpi di uguaglianza e libertà di partecipazione.</p>

<h2>Come si arriva alla Corte</h2>
<p>Sarno è realista: non basta un ricorso il giorno dopo la firma della legge. La Consulta pretende un danno concreto e attuale, non solo ipotetico; con le elezioni lontane, un ricorso prematuro verrebbe respinto. La strada solida è un fronte articolato — elettori, nuove formazioni, candidati — sul modello dell'azione che nel 2014 aprì la breccia. Con un limite ancora aperto: manca una tutela rapida, prima del voto, per contestare firme, simboli e ammissione delle liste davanti a un giudice terzo.</p>

<h2>Perché ne parliamo</h2>
<p>Non è tifo per una parte contro l'altra. La legge, avverte Sarno, difficilmente cadrà tutta: più probabile un colpo mirato della Corte sul premio fisso, sulle liste bloccate, sulle candidature multiple, sui voti sotto soglia. Il problema non è una singola norma, ma il modo in cui tutti questi meccanismi si sommano.</p>

<p>E il punto, per noi, è sempre lo stesso: che il voto continui a esprimere liberamente la rappresentanza, e non serva a costruire in anticipo — per automatismi di legge — una maggioranza già decisa e parlamentari scelti dagli apparati. Su come si vota non esistono spettatori. Noi continueremo a seguirlo, passaggio dopo passaggio.</p>

<p style="font-style:italic;font-size:.88em;color:#888;margin-top:28px">Analisi giuridica completa: Beppe Sarno, «Le crepe costituzionali della nuova legge elettorale», <a href="https://www.criticasociale.net/articolo-primo-piano-it.php?id=57" target="_blank" rel="noopener nofollow">Critica Sociale</a>.</p>

</article>
'''

BODY_APE = '''
<style>
.pa-hero-img{display:block;max-width:100%;border-radius:18px;box-shadow:0 10px 30px rgba(0,0,0,.15);margin:0 0 28px}
.pa-lead{font-size:1.12em!important;color:#8a4e00!important;font-weight:600}
.pa-fig{margin:32px 0}
.pa-fig video{width:100%;max-width:480px;display:block;margin:0 auto;border-radius:14px;box-shadow:0 6px 20px rgba(0,0,0,.12)}
.pa-fig figcaption{font-family:montserrat,sans-serif;font-size:.85em;color:#9c5b00;margin-top:14px;text-align:center;font-weight:700;max-width:620px;margin-left:auto;margin-right:auto;line-height:1.5}
.pa-box{background:#fff8ee;border:2px solid #ffd580;border-radius:16px;padding:24px 28px;margin:28px 0}
.pa-box h3{font-family:montserrat,sans-serif;color:#9c5b00;font-size:1em;font-weight:800;text-transform:uppercase;letter-spacing:.5px;margin:0 0 10px}
.pa-tbl{width:100%;border-collapse:collapse;margin:22px 0;font-family:montserrat,sans-serif;font-size:.86em}
.pa-tbl th,.pa-tbl td{border:1px solid #f0e6d3;padding:9px 12px;text-align:left;vertical-align:top}
.pa-tbl thead th{background:#8a4e00;color:#fff;font-weight:700}
.pa-tbl tbody th{background:#fff8ee;color:#8a4e00;font-weight:700}
.pa-stat{display:flex;flex-wrap:wrap;gap:14px;margin:26px 0}
.pa-stat .s{flex:1 1 220px;background:#fff8ee;border-radius:12px;padding:18px 20px}
.pa-stat .n{font-family:merriweather,serif;font-size:1.8em;font-weight:900;line-height:1;color:#8a4e00}
.pa-stat .l{font-size:.82em;color:#555;margin-top:6px;font-family:montserrat,sans-serif;line-height:1.5}
.pa-dl{display:flex;align-items:center;gap:16px;border:2px solid #e8900a;border-radius:14px;padding:20px 22px;margin:30px 0;background:#fff8ee}
.pa-dl .ico{flex:0 0 auto;width:46px;height:46px;border-radius:10px;background:#8a4e00;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:.72em;font-family:montserrat,sans-serif}
.pa-dl .t{flex:1 1 auto;font-family:montserrat,sans-serif;font-size:.84em;color:#555;line-height:1.5}
.pa-dl .t b{color:#8a4e00;display:block;margin-bottom:3px}
.pa-dl a.btn{flex:0 0 auto;background:#e8900a;color:#fff;text-decoration:none;padding:11px 20px;border-radius:50px;font-family:montserrat,sans-serif;font-weight:700;font-size:.84em}
.pa-confini{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin:24px 0}
.pa-confini div{background:#fff8ee;border-left:4px solid #e8900a;border-radius:0 10px 10px 0;padding:16px 18px;font-size:.88em;color:#444;line-height:1.6}
.pa-confini strong{color:#8a4e00;display:block;margin-bottom:4px}
</style>

<article class="article-wrap">

<img class="pa-hero-img" src="images/ape-copertina.webp" alt="APE — Assemblea Popolare Ecumenica: un canale permanente di voce dei cittadini. Angelo Nicotra, Partecipazione Attiva">

<p class="pa-lead">Con APE (Assemblea Popolare Ecumenica), Partecipazione Attiva lancia una nuova idea di Democrazia Partecipativa per rendere i cittadini parte attiva nella gestione politica del nostro Paese.</p>

<p>È la proposta di legge più importante del movimento: una riforma costituzionale che non aggiunge un partito né un candidato, ma uno strumento permanente attraverso cui ogni cittadino può obbligare le istituzioni ad ascoltare e a rispondere. Elaborata da Angelo Nicotra, Presidente di Partecipazione Attiva, ed è oggi proposta ufficiale del movimento.</p>

<div class="pa-fig">
<video controls preload="metadata" playsinline poster="images/ape-copertina.webp">
<source src="video/ape-tocca-a-noi.mp4" type="video/mp4">
Il tuo browser non supporta il video.
</video>
<figcaption>Con APE (Assemblea Popolare Ecumenica), Partecipazione Attiva lancia una nuova idea di Democrazia Partecipativa per rendere i cittadini parte attiva nella gestione politica del nostro Paese.</figcaption>
</div>

<div class="pa-dl">
<div class="ico">PDF</div>
<div class="t"><b>Il documento integrale</b>25 pagine: articolato costituzionale, allegati tecnici, obiezioni e risposte, confronto con le esperienze estere. Approvato dal direttivo.</div>
<a class="btn" href="documenti/APE_Assemblea_Popolare_Ecumenica_v6.8.pdf" target="_blank" rel="noopener">Scarica il PDF</a>
</div>

<h2>Il problema che l'APE vuole risolvere</h2>
<p>Tra un'elezione e l'altra, per cinque anni, il cittadino non ha più voce. La democrazia italiana funziona per delega: si vota, si affida il mandato a chi è eletto, e fino al voto successivo la partecipazione è di fatto sospesa. Il modello ha retto finché esistevano i corpi intermedi — partiti di massa, sindacati, associazioni capillari — che tenevano aperto un canale permanente tra società e istituzioni. Quei corpi si sono dissolti.</p>

<div class="pa-stat">
<div class="s"><div class="n">39,84%</div><div class="l">degli aventi diritto non si è recato alle urne alle politiche del 25 settembre 2022 (36,34% considerando i soli residenti in Italia): il minimo storico assoluto della Repubblica</div></div>
</div>

<p>Non è apatia: gli studi mostrano che è rifiuto consapevole di un sistema percepito come distante e non più influenzabile. L'APE non sostiene che «il sistema ha fallito, quindi va rimpiazzato» — sarebbe una tesi sbagliata e pericolosa. Sostiene qualcosa di più modesto e più solido: manca un meccanismo istituzionale che mantenga viva la voce dei cittadini nel tempo che intercorre tra le elezioni, e che obblighi le istituzioni a prendere posizione su quella voce invece di ignorarla.</p>

<h2>Cos'è l'APE, e cosa non è</h2>
<p>Prima di descrivere cosa fa l'APE, è più importante fissare con precisione cosa l'APE <em>non</em> fa e non potrà mai fare — è proprio da questi confini che dipende la sua legittimità costituzionale.</p>

<div class="pa-confini">
<div><strong>Non legifera.</strong> Non approva leggi, non abroga norme. La funzione legislativa resta integralmente del Parlamento.</div>
<div><strong>Non governa.</strong> Non adotta provvedimenti amministrativi, non nomina, non gestisce risorse pubbliche.</div>
<div><strong>Non vincola il voto del parlamentare.</strong> Nessun suo atto introduce un vincolo di mandato.</div>
<div><strong>Non sostituisce alcun organo.</strong> Non prende il posto del Senato, della Camera, delle Regioni o dei Comuni: è aggiuntiva, non un rimpiazzo.</div>
<div><strong>Non ha carriere né poteri permanenti.</strong> Nessun membro acquisisce posizioni di vantaggio o canali privilegiati.</div>
</div>

<p>La sua forza è procedurale e reputazionale, non giuridico-sanzionatoria. Gli atti dell'Assemblea Popolare producono effetti esclusivamente procedurali: attivano il dovere dell'istituzione destinataria di esaminare l'istanza e di pronunciarsi con relazione motivata e pubblica. Non producono effetti normativi diretti né vincolano nel merito il contenuto delle leggi o i singoli voti parlamentari.</p>

<h2>Il sorteggio, non l'elezione</h2>
<p>I componenti dell'APE sono scelti per sorteggio fra i cittadini, mai per elezione — è la scelta più identitaria del progetto, e anche la più contro-intuitiva. L'elezione, per quanto democratica, produce inevitabilmente ciò che si vuole tenere fuori dall'APE: candidature, campagne, raccolta di consenso, schieramenti, carriere. Il sorteggio, al contrario, produce uno specchio statistico della popolazione: persone comuni che portano il punto di vista reale del Paese, non quello filtrato dagli apparati — lo stesso principio già in uso nei giudici popolari delle Corti d'Assise.</p>
<p>L'estrazione avviene dalle liste elettorali, con stratificazione per età, genere e territorio, così che lo specchio sia fedele. La partecipazione è volontaria nel senso che chi è estratto può rinunciare, ma la base di estrazione è l'intero corpo elettorale, non un registro di volontari.</p>

<h2>Tre livelli orizzontali, nessuna gerarchia</h2>
<p>L'APE si articola su tre livelli — comunale (<strong>APEC</strong>), regionale (<strong>APER</strong>) e nazionale (<strong>APEN</strong>) — ma questi non sono gradini di una scala: nessun livello comanda sull'altro. Sono microfoni accordati ciascuno al proprio interlocutore istituzionale: l'APEC parla al Comune, l'APER alla Regione, l'APEN allo Stato. Un'istanza sale di livello solo quando emerge in modo ricorrente su più territori diversi, o quando riguarda una materia di competenza esclusiva di un livello superiore — mai per decisione discrezionale di un "centro".</p>
<p>Nel canale che porta le istanze territoriali verso il livello nazionale, ogni territorio ha pari rappresentanza, indipendentemente dalla popolazione: è una garanzia contro la discriminazione, non un favore ai piccoli comuni — nessun cittadino deve pesare meno nel farsi ascoltare per il solo fatto di vivere in un luogo meno popoloso.</p>

<h2>Il ciclo dell'istanza: voce, risposta, verifica, referendum</h2>
<p>È il cuore operativo del progetto: come una richiesta nasce dal cittadino, percorre l'APE, raggiunge l'istituzione e ne ottiene una risposta — e cosa succede quando la risposta manca, è negativa, o resta sulla carta.</p>
<ol style="color:#444;line-height:2;padding-left:20px;font-family:merriweather,serif">
<li><strong>Voce.</strong> Il cittadino deposita un'istanza; l'APE competente la riceve, la istruisce e la formalizza.</li>
<li><strong>Dovere di esame.</strong> L'istituzione destinataria ha il dovere di prenderla in carico e di non lasciarla cadere nel silenzio.</li>
<li><strong>Relazione motivata pubblica.</strong> L'istituzione si pronuncia con una relazione pubblica che dice sì o no e ne espone le ragioni.</li>
<li><strong>Verifica dell'attuazione.</strong> Entro un anno, l'istituzione riferisce pubblicamente sullo stato di attuazione di ciò che ha accolto.</li>
<li><strong>In caso di rifiuto o di stallo.</strong> Si apre la via del referendum propositivo: la decisione torna ai cittadini.</li>
</ol>
<p>Il referendum propositivo è la leva dura del sistema — l'unica — attivabile solo a procedimento ordinario esaurito, e costruito in tre stadi: pronuncia parlamentare obbligatoria, raccolta firme a soglia oggettiva se il Parlamento non recepisce, e infine il referendum, valido senza quorum di partecipazione quando i voti favorevoli superano un quarto degli aventi diritto al voto — circa 12,5 milioni di "sì" su un corpo elettorale di 50 milioni: alta, ma raggiungibile da una mobilitazione reale, e immune al boicottaggio per assenteismo che affligge il quorum classico.</p>

<h2>Indennità e permessi di lavoro</h2>
<p>Perché la partecipazione sia davvero aperta a tutti — e non solo a chi può dedicarvi tempo gratuitamente — chi è sorteggiato riceve un'indennità e ha diritto a permessi di lavoro retribuiti. Senza copertura del reddito perduto, l'orizzontalità diventerebbe una finzione: l'assemblea si distorcerebbe verso i ceti abbienti, diventando lo specchio di chi può permetterselo invece che del Paese reale.</p>

<h2>Una proposta distinta: l'abolizione del Senato</h2>
<p>Il progetto include, su un binario separato e indipendente, anche l'abolizione del Senato — una riforma che non dipende in alcun modo dall'esistenza dell'APE, e viceversa. Le due cose restano volutamente slegate: se una delle due proposte si ferma in Parlamento, l'altra prosegue per conto suo.</p>

<h2>Difese contro lo svuotamento e contro il carrozzone</h2>
<p>Chi legge questo progetto ha due timori legittimi e opposti: che l'APE venga svuotata e resa innocua da una maggioranza ostile, oppure che cresca fino a diventare un nuovo carrozzone costoso e autoreferenziale. Una clausola di non-regressione impedisce che una legge ordinaria riduca le garanzie e i poteri di voce dell'APE al di sotto del livello costituzionale. Sul fronte opposto, un Collegio di Garanzia vigila su regolarità del sorteggio, trasparenza e congruità delle risposte — ma non ha potere sanzionatorio proprio: accerta, sospende in via cautelare gli atti viziati, e trasmette all'autorità competente, che è obbligata ad aprire il procedimento e concluderlo con atto motivato.</p>

<h2>I costi, detti con onestà</h2>
<p>Un organo di partecipazione ha un costo reale, dichiarato senza abbellimenti: indennità ai sorteggiati, permessi di lavoro, uffici territoriali, piattaforma digitale, trasparenza in streaming.</p>

<div class="pa-stat">
<div class="s"><div class="n">≈36,2 mln €</div><div class="l">stima annua a regime, per l'intera struttura APEC + APER + APEN, Collegio di Garanzia incluso</div></div>
<div class="s"><div class="n">0,67%</div><div class="l">di quanto costa oggi la sola Presidenza del Consiglio (5,4 miliardi €/anno nel 2025) — e una frazione minima del bilancio statale complessivo</div></div>
<div class="s"><div class="n">9.830</div><div class="l">cittadini sorteggiati in totale nell'ipotesi illustrativa, contro i ~46.000 di impostazioni capillari alternative: un sistema deliberatamente snello</div></div>
</div>

<h2>Cosa insegna il mondo</h2>
<p>Il modello APE non nasce nel vuoto: dialoga con le esperienze di democrazia partecipativa già sperimentate altrove, prendendone i pregi ed evitandone gli errori.</p>

<table class="pa-tbl">
<thead><tr><th>Esperienza</th><th>Cosa insegna all'APE</th></tr></thead>
<tbody>
<tr><th>Irlanda — Citizens' Assembly (2016-2018)</th><td>Un'assemblea di cittadini sorteggiati può affrontare temi divisivi e produrre proposte che il sistema recepisce. Conferma la praticabilità del sorteggio.</td></tr>
<tr><th>Belgio — Ostbelgien (dal 2019)</th><td>Primo Consiglio dei cittadini permanente per legge, con dovere delle istituzioni di rispondere e di rendicontare l'attuazione a un anno.</td></tr>
<tr><th>Francia — Convention Citoyenne (2019-2020)</th><td>Lezione cautelativa: raccogliere la voce e poi disattenderla senza risposta chiara la fa fallire. Da qui l'obbligo di relazione motivata, la verifica a un anno e il referendum come ultima istanza.</td></tr>
<tr><th>Italia — giudici popolari</th><td>Il sorteggio per una funzione pubblica delicata è già nel nostro ordinamento e funziona. L'APE ne estende il principio.</td></tr>
</tbody>
</table>

<p>Va detto con chiarezza cosa la Convention Citoyenne francese dimostra e cosa no: non dimostra che il sorteggio non funziona — dimostra che il sorteggio senza obbligo di risposta e senza sbocco è teatro. L'APE aggiunge esattamente le cose che alla Francia mancavano.</p>

<div class="pa-dl">
<div class="ico">PDF</div>
<div class="t"><b>Leggi il progetto completo</b>Articolato costituzionale integrale, i 15 confronti con le obiezioni più dure, il dettaglio dei costi e il cronoprogramma.</div>
<a class="btn" href="documenti/APE_Assemblea_Popolare_Ecumenica_v6.8.pdf" target="_blank" rel="noopener">Scarica il PDF</a>
</div>

<h2>La Rete APE</h2>
<p>Partecipazione Attiva ha aperto una rete che invita altre associazioni, movimenti e comitati civici a condividere questi principi, con peso paritario per ogni soggetto aderente: nessuna gerarchia tra chi aderisce, indipendentemente dalla dimensione o dalla storia di ciascuno.</p>
<p><a href="rete-ape.html" style="color:#9c5b00;font-weight:700">→ Scopri la Rete APE e come aderire</a></p>

<div class="pa-box">
<h3>Il documento, in una frase</h3>
<p style="color:#555;font-size:.92em;line-height:1.7;margin:0">L'APE non promette che le proposte dei cittadini vengano approvate — sarebbe falso. Promette qualcosa di più solido e verificabile: che nessuna proposta possa essere diluita o sepolta nel silenzio, che ciò che è accolto sia poi verificato in pubblico, e che chi è respinto abbia una via d'uscita reale.</p>
</div>

<p class="pa-lead">Non un salvatore. Noi. I leader di noi stessi. Il documento integrale, con l'articolato costituzionale completo e tutte le garanzie, è disponibile per il download in questa pagina.</p>

</article>
'''

ART_STABILICUM_CREPE = {
  'slug'         : 'stabilicum-crepe-costituzionali-17lug2026.html',
  'autore'       : 'pa',
  'data_iso'     : '2026-07-17',
  'data_human'   : '17 luglio 2026',
  'data_badge'   : '17 LUGLIO 2026',
  'lettura_min'  : 5,
  'categoria_hero': '⚖️ Riforma elettorale',
  'og_image'     : 'images/pensattivo-stabilicum.webp',
  'h1'           : 'Stabilicum, la legge che rischia la bocciatura: cosa dice chi la porterà davanti alla Corte',
  'sottotitolo'  : 'Un’analisi giuridica individua sette profili di sospetta incostituzionalità nel testo approvato dalla Camera. Il testo passa ora al Senato, in attesa del giudizio della Consulta.',
  'meta_desc'    : 'Sette profili di incostituzionalità nello Stabilicum secondo l’avvocato Beppe Sarno: premio fisso, liste bloccate, firme, premierato di fatto.',
  'card_cat'     : 'RIFORMA ELETTORALE',
  'card_title'   : 'Stabilicum, la legge che rischia la bocciatura',
  'card_desc'    : 'Un’analisi giuridica individua sette profili di incostituzionalità nello Stabilicum. Il testo passa ora al Senato.',
  'ticker_emoji' : '⚖️',
  'ticker_tema'  : 'STABILICUM',
  'ticker_testo' : 'un’analisi giuridica individua sette profili di incostituzionalità nello Stabilicum prima del passaggio al Senato',
  'body'         : BODY_STABILICUM_CREPE,
}
# ===========================================================================

ART = {
  'slug'         : 'ape.html',
  'autore'       : 'nicotra',
  'data_iso'     : '2026-07-22',
  'data_human'   : '22 luglio 2026',
  'data_badge'   : '22 LUGLIO 2026',
  'lettura_min'  : 9,
  'categoria_hero': '\U0001F41D Proposta di Legge',
  'og_image'     : 'images/ape-og.jpg',
  'h1'           : 'APE — Assemblea Popolare Ecumenica',
  'sottotitolo'  : 'La proposta di Partecipazione Attiva per un canale permanente di voce dei cittadini, oltre la democrazia delegativa.',
  'meta_desc'    : 'Con APE, Partecipazione Attiva propone un’assemblea permanente di cittadini sorteggiati che obbliga le istituzioni a rispondere: come funziona, cosa non fa, quanto costa.',
  'card_cat'     : 'PROPOSTA DI LEGGE',
  'card_title'   : 'APE — Assemblea Popolare Ecumenica',
  'card_desc'    : 'La più grande proposta di Partecipazione Attiva: un canale permanente di voce dei cittadini, con i sorteggiati che le istituzioni sono obbligate ad ascoltare.',
  'ticker_emoji' : '\U0001F41D',
  'ticker_tema'  : 'APE',
  'ticker_testo' : 'Partecipazione Attiva lancia l’Assemblea Popolare Ecumenica: la proposta che dà ai cittadini una voce permanente',
  'body'         : BODY_APE,
}
# ===========================================================================

GOLD = BASE + 'template.html'
IDX  = BASE + 'index.html'
SMP  = BASE + 'sitemap.xml'
TEMI = BASE + 'temi.json'
MAX_TICKER = 8   # tetto voci ticker (auto-pulizia delle piu' vecchie)

VIETATE = ['SIRE', 'Camera dei Deputati', 'luigi-spanu.jpg', 'Evento alla Camera', 'spanu-sire']

def build_articolo(a):
    nome, ruolo, foto = AUTORI[a['autore']]
    html = open(GOLD, encoding='utf-8').read()
    assert html.count('type=application/ld+json') == 0, 'GOLD ha schema fantasma'
    U = 'https://partecipazione-attiva.it/'
    html = re.sub(r'<title>[^<]*</title>', f"<title>{a['h1']} | {nome}</title>", html, 1)
    html = re.sub(r'<meta name="description" content="[^"]*">', f"<meta name=\"description\" content=\"{a['meta_desc']}\">", html, 1)
    html = re.sub(r'<meta property="og:title" content="[^"]*">', f"<meta property=\"og:title\" content=\"{a['h1']}\">", html, 1)
    html = re.sub(r'<meta property="og:description" content="[^"]*">', f"<meta property=\"og:description\" content=\"{a['meta_desc']}\">", html, 1)
    html = re.sub(r'<meta property="og:url" content="[^"]*">', f"<meta property=\"og:url\" content=\"{U}{a['slug']}\">", html, 1)
    html = re.sub(r'<link rel="alternate" hreflang="it" href="[^"]*">', f"<link rel=\"alternate\" hreflang=\"it\" href=\"{U}{a['slug']}\">", html, 1)
    html = re.sub(r'<link rel="canonical" href="[^"]*">', f"<link rel=\"canonical\" href=\"{U}{a['slug']}\">", html, 1)
    html = re.sub(r'<meta property="og:image" content="[^"]*">', f"<meta property=\"og:image\" content=\"{U}{a['og_image']}\">", html, 1)
    html = html.replace('</title>', '</title>' + f'<meta property="og:article:published_time" content="{a["data_iso"]}T00:00:00+02:00">', 1) if 'og:article:published_time' not in html else html
    schema = {"@context":"https://schema.org","@type":"NewsArticle","headline":a['h1'],
              "description":a['meta_desc'],"image":U+a['og_image'],"datePublished":a['data_iso'],
              "dateModified":a['data_iso'],
              "author":{"@type":"Person","@id":U+"organigramma.html#"+a['autore'],"name":nome,"jobTitle":ruolo,"url":U+"organigramma.html"},
              "publisher":{"@type":"Organization","name":"Partecipazione Attiva",
                           "logo":{"@type":"ImageObject","url":U+"LOGO-PA.webp"}},
              "mainEntityOfPage":U+a['slug']}
    html = re.sub(r'<script type="application/ld\+json">.*?</script>',
                  '<script type="application/ld+json">'+json.dumps(schema, ensure_ascii=False)+'</script>',
                  html, flags=re.DOTALL, count=1)
    # BreadcrumbList: Home > {card_cat|Battaglie} > {h1}
    brc_mid = a.get('card_cat') or 'Battaglie'
    breadcrumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":U},
        {"@type":"ListItem","position":2,"name":brc_mid,"item":U+"battaglie.html"},
        {"@type":"ListItem","position":3,"name":a['h1'],"item":U+a['slug']}]}
    html = html.replace('</head>',
        '<script type="application/ld+json">'+json.dumps(breadcrumb, ensure_ascii=False)+'</script></head>', 1)
    brc_mid = a.get('card_cat') or 'Battaglie'
    brc_vis = (f'<nav class="breadcrumb" aria-label="Percorso" style="max-width:820px;margin:0 auto;padding:14px 24px 0;'
               f'font-family:montserrat,sans-serif;font-size:.82em;color:#9c5b00">'
               f'<a href="index.html" style="color:#9c5b00;text-decoration:none">Home</a>'
               f' <span aria-hidden="true">&rsaquo;</span> '
               f'<a href="battaglie.html" style="color:#9c5b00;text-decoration:none">{brc_mid}</a>'
               f' <span aria-hidden="true">&rsaquo;</span> '
               f'<span style="color:#8a4e00">{a["card_title"]}</span></nav>')
    hero = (brc_vis + f'<div class="article-hero">\n  <div class="categoria">{a["categoria_hero"]}</div>\n'
            f'  <h1>{a["h1"]}</h1>\n  <p class="sottotitolo">{a["sottotitolo"]}</p>\n'
            f'  <div class="author-hero">\n    <img loading=lazy src="{foto}" alt="{nome} {ruolo} Partecipazione Attiva">\n'
            f'    <div class="author-hero-info">\n      <div class="nome">{nome}</div>\n'
            f'      <div class="ruolo">{ruolo} &mdash; Partecipazione Attiva</div>\n    </div>\n  </div>\n'
            f'  <div class="article-meta">\n    <span class="badge-pa">Partecipazione Attiva</span>\n'
            f'    <span>&#x1F4C5; {a["data_human"]}</span>\n    <span>&#x23F1; {a["lettura_min"]} minuti di lettura</span>\n  </div>\n</div>')
    body = a['body']
    if not body.lstrip().startswith('<article'):
        body = '<article class="article-wrap">\n' + body + '\n</article>'
    # link di condivisione corretti dentro il corpo (se l'autore non li mette)
    start = html.index('<div class="article-hero">')
    end   = html.index('</article>') + len('</article>')
    html  = html[:start] + '<main id="contenuto">' + hero + '\n\n' + body + '</main>' + html[end:]
    # bonifica residui share GOLD
    for bad in ['u=https://partecipazione-attiva.it/spanu-sire.html', '%20https://partecipazione-attiva.it/spanu-sire.html']:
        html = html.replace(bad, bad.replace('spanu-sire.html', a['slug']))
    # rimuovi schema FAQ del GOLD (blocco JSON-LD FAQPage residuo, contiene stringhe vietate)
    import re as _re
    html = _re.sub(r'<script type="application/ld\+json">\s*\{[^<]*?FAQPage.*?</script>', '', html, flags=_re.DOTALL)
    html = html.replace('https://partecipazioneattiva.github.io/', U).replace('partecipazioneattiva.github.io', 'partecipazione-attiva.it')
    for _t,_v in [('{{TITLE}}',a['h1']),('{{H1}}',a['h1']),('{{META_DESC}}',a['meta_desc']),('{{SOTTOTITOLO}}',a['sottotitolo']),('{{CATEGORIA}}',a['categoria_hero']),('{{OG_IMAGE}}',U+a['og_image'])]:
        html = html.replace(_t,_v)
    return html

def check_articolo(path):
    h = open(path, encoding='utf-8').read()
    errs = []
    if not h.rstrip().endswith('</html>'): errs.append('file troncato')
    if 'github.io' in h: errs.append('github.io presente')
    if 'type=application/ld+json' in h: errs.append('schema fantasma')
    for v in VIETATE:
        if v in h: errs.append(f'residuo GOLD: {v}')
    if h.count('<script type="application/ld+json">') != 2: errs.append('schema: attesi 2 blocchi (NewsArticle + BreadcrumbList)')
    return errs

BADGE = ('<span style="display:inline-block;background:#c0392b;color:#fff;font-size:0.69em;'
         'font-weight:900;letter-spacing:1px;text-transform:uppercase;padding:3px 10px;'
         'border-radius:50px;margin-bottom:6px;animation:pulse-live 1.2s infinite">Ultimo aggiornamento</span><br>')

def card_html(a):
    return (f'<a href="{a["slug"]}" data-pa-section="homepage-card" style="display:flex;align-items:stretch;'
            'border-radius:16px;overflow:hidden;background:rgba(255,255,255,.12);border:2px solid #ffd580;'
            'text-decoration:none;margin-bottom:14px;min-height:180px">'
            f'<img src="{a["og_image"]}" alt="{a["card_cat"]}" style="width:140px;min-height:180px;'
            'object-fit:cover;flex-shrink:0;display:block">'
            '<div style="padding:16px 18px;display:flex;flex-direction:column;justify-content:space-between"><div>'
            + BADGE +
            f'<span style="font-family:montserrat,sans-serif;font-size:.72em;font-weight:700;color:#ffd580;'
            f'letter-spacing:1px;text-transform:uppercase">{a["card_cat"]}</span>'
            f'<h3 style="font-family:montserrat,sans-serif;font-size:1em;font-weight:700;color:#fff;'
            f'margin:6px 0 8px;line-height:1.35">{a["card_title"]}</h3>'
            f'<p style="font-family:merriweather,serif;font-size:.82em;color:rgba(255,255,255,.82);'
            f'line-height:1.55;margin:0">{a["card_desc"]}</p></div>'
            f'<span style="font-family:montserrat,sans-serif;font-size:.75em;color:#ffd580;font-weight:700;'
            f'margin-top:10px">&#x1F195; {a["data_badge"]}</span></div></a>')

def pulisci_badge_vecchi(html, data_badge_oggi):
    # rimuove il badge rosso dalle card la cui data badge != oggi (regola: badge = solo giorno di pubblicazione)
    def repl(m):
        seg = m.group(0)
        if 'pulse-live' in seg and f'&#x1F195; {data_badge_oggi}' not in seg:
            seg = seg.replace(BADGE, '')
        return seg
    return re.sub(r'<a (?![^>]*data-pa-pin)[^>]*data-pa-section="homepage-card".*?</a>', repl, html, flags=re.DOTALL)

def aggiorna_index(a):
    html = open(IDX, encoding='utf-8').read()
    assert a['slug'] not in html, 'STOP: card gia presente (gia pubblicato?)'
    # 1) inserisci la nuova card PRIMA della prima card NON pinnata.
    #    Le card con data-pa-pin="1" (es. la Mappa) restano sempre in cima.
    m = re.search(r'<a (?![^>]*data-pa-pin)[^>]*data-pa-section="homepage-card"', html)
    assert m, 'STOP: nessuna card homepage trovata'
    pos = m.start()
    html = html[:pos] + card_html(a) + html[pos:]
    # 2) regola badge: togli il badge dalle card di giorni diversi da oggi
    html = pulisci_badge_vecchi(html, a['data_badge'])
    open(IDX, 'w', encoding='utf-8').write(html)

def aggiorna_temi(a):
    # inserisce la voce del nuovo articolo in cima a temi.json, dedup per tema, tetto MAX_TICKER
    try:
        d = json.load(open(TEMI, encoding='utf-8'))
    except FileNotFoundError:
        d = {'voci': []}
    voci = [v for v in d.get('voci', []) if v.get('tema') != a['ticker_tema']]  # dedup per tema
    voci.insert(0, {'emoji': a['ticker_emoji'], 'tema': a['ticker_tema'], 'testo': a['ticker_testo']})
    d['voci'] = voci[:MAX_TICKER]   # in cima + auto-pulizia
    json.dump(d, open(TEMI, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    return f"temi.json: voce '{a['ticker_tema']}' in cima ({len(d['voci'])}/{MAX_TICKER} voci)"

def aggiorna_sitemap(a):
    sm = open(SMP, encoding='utf-8').read()
    if a['slug'] in sm:
        return 'sitemap: gia presente'
    row = f'<url><loc>https://partecipazione-attiva.it/{a["slug"]}</loc><lastmod>{a["data_iso"]}</lastmod></url>'
    assert sm.count('</urlset>') == 1, 'STOP: </urlset> non singolo'
    open(SMP, 'w', encoding='utf-8').write(sm.replace('</urlset>', row + '\n</urlset>', 1))
    return 'sitemap: url aggiunto'

def main():
    a = ART
    out = BASE + a['slug']
    assert not os.path.exists(out), f'STOP: {a["slug"]} esiste gia'
    html = build_articolo(a)
    open(out, 'w', encoding='utf-8').write(html)
    errs = check_articolo(out)
    assert not errs, 'CHECK FALLITI: ' + '; '.join(errs)
    print(f'OK articolo: {a["slug"]} ({len(html)} char) - 8 check superati')
    aggiorna_index(a)
    print('OK index.html: card in cima + badge per-data')
    print('OK ' + aggiorna_temi(a))
    print('OK ' + aggiorna_sitemap(a))
    print('--- FATTO. Esegui il PUSH: include aggiorna_ticker.py che rigenera la barra da temi.json ---')

if __name__ == '__main__':
    main()
