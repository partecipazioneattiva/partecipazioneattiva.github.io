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
    'nicotra':  ('Angelo Nicotra','Presidente','images/organigramma/angelo-nicotra.webp'),
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

ART = {
  'slug'         : 'cavalleggeri-cielo-aperto.html',
  'autore'       : 'pa',
  'data_iso'     : '2026-07-05',
  'data_human'   : '5 luglio 2026',
  'data_badge'   : '5 LUGLIO 2026',
  'lettura_min'  : 4,
  'categoria_hero': '\U0001F3A8 Riqualificazione Urbana',
  'og_image'     : 'images/cavalleggeri-museo.webp',
  'h1'           : 'Cavalleggeri a cielo aperto: un museo di murales per Fuorigrotta',
  'sottotitolo'  : 'La proposta di Partecipazione Attiva per Via Marco Polo, agganciata all\u2019America\u2019s Cup 2027 e alla rigenerazione di Bagnoli.',
  'meta_desc'    : 'Partecipazione Attiva propone al Comune di Napoli un museo diffuso di street art a Cavalleggeri d\u2019Aosta, Fuorigrotta: decoro, identit\u00e0 e leva economica per il quartiere.',
  'card_cat'     : 'RIQUALIFICAZIONE URBANA',
  'card_title'   : 'Cavalleggeri a cielo aperto: un museo di murales per Fuorigrotta',
  'card_desc'    : 'La proposta di PA per Via Marco Polo, agganciata all\u2019America\u2019s Cup 2027 e alla rigenerazione di Bagnoli.',
  'ticker_emoji' : '\U0001F3A8',
  'ticker_tema'  : 'CAVALLEGGERI',
  'ticker_testo' : 'un museo di murales a cielo aperto per Fuorigrotta: la proposta di PA al Comune di Napoli',
  'body'         : BODY_CAVALLEGGERI,
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
