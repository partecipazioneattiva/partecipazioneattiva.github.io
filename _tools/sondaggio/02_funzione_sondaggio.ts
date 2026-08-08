// =====================================================================
// FUNZIONE "sondaggio" - Partecipazione Attiva - 8 agosto 2026
// =====================================================================
// Si installa in Supabase come Edge Function di nome esattamente:
//     sondaggio
// (istruzioni passo per passo in LEGGIMI.md, accanto a questo file)
//
// FA DUE MESTIERI, decisi dal campo "azione":
//
//   (nessuna azione)  RICEVE UN VOTO
//     1. controlla che i temi siano fra i sei (scelta multipla libera) e
//        che ci sia almeno un tema OPPURE una frase scritta a mano;
//     2. chiede all'archivio di registrare il voto IN ATTESA - e' l'archivio
//        a rimescolare l'indirizzo col segreto, qui non passa mai;
//     3. manda la mail di conferma con Brevo;
//     4. risponde al sito SENZA mai dargli il codice di conferma: se lo
//        desse, chiunque potrebbe confermarsi da solo.
//
//   azione: "conferma"   CONTA IL VOTO
//     5. conta il voto e cancella l'indirizzo;
//     6. se la persona ha scritto qualcosa nella casella "altro", MANDA
//        QUELLA FRASE AL MOVIMENTO per posta. E' l'unico modo in cui una
//        frase esce dall'archivio: al sito non torna mai.
//
// Perche' la conferma passa di qui e non piu' direttamente dall'archivio:
// perche' la frase la deve leggere il server per spedirla, e il sito non
// deve poterla vedere.
//
// NON contiene chiavi. Le legge dai segreti del progetto.
// =====================================================================

const SITO = "https://partecipazione-attiva.it";

// A chi arrivano le frasi scritte nella casella "altro".
const AVVISI_A = Deno.env.get("SONDAGGIO_AVVISI_A") ??
  "webmaster.partecipazione.attiva@gmail.com";

// IL MITTENTE. Attenzione alla trappola: sulle mail gia' spedite Gmail mostra
// come mittente un indirizzo @NUMERO.brevosend.com, ma quello NON e' il mittente
// da dichiarare - e' quello che Brevo ci mette al posto suo, perche' Gmail non
// permette di spedire "a nome di" un indirizzo @gmail.com. Dichiarando quello
// Brevo risponde "Sending has been rejected because the sender you used...".
// Va dichiarato l'indirizzo VERO, quello validato nell'account Brevo.
const MITTENTE_EMAIL =
  Deno.env.get("BREVO_MITTENTE") ??
  "webmaster.partecipazione.attiva@gmail.com";
const MITTENTE_NOME = "Partecipazione Attiva";
const RISPONDI_A = "webmaster.partecipazione.attiva@gmail.com";

// Il nome del segreto puo' cambiare da progetto a progetto: li provo tutti.
const CHIAVE_BREVO =
  Deno.env.get("BREVO_API_KEY") ??
  Deno.env.get("BREVO_KEY") ??
  Deno.env.get("SENDINBLUE_API_KEY") ??
  Deno.env.get("BREVO");

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const TEMI: Record<string, string> = {
  "ape": "APE &mdash; l&rsquo;Assemblea Popolare Ecumenica",
  "mappa": "La Mappa dei cittadini attivi",
  "legge-elettorale": "La legge elettorale",
  "rc-auto": "RC Auto",
  "arte-del-dono": "L&rsquo;arte del dono",
  "donna-a-napoli": "Essere donna a Napoli",
};

/**
 * LA CHIAVE CON CUI IL SERVER PARLA AL PROPRIO ARCHIVIO.
 *
 * Dal 2026 Supabase ha cambiato sistema di chiavi. Quella vecchia
 * (SUPABASE_SERVICE_ROLE_KEY) e' dichiarata OBSOLETA - nel pannello compare
 * proprio con l'etichetta DEPRECATED - e al suo posto c'e' SUPABASE_SECRET_KEYS,
 * che NON e' una stringa ma un elenco in JSON da cui si prende la voce 'default'.
 * Qui si prova prima la nuova e poi la vecchia.
 */
function chiaveDelServer(): string | null {
  try {
    const nuove = Deno.env.get("SUPABASE_SECRET_KEYS");
    if (nuove) {
      const d = JSON.parse(nuove);
      const k = d["default"] ?? Object.values(d)[0];
      if (typeof k === "string" && k) return k;
    }
  } catch (e) {
    console.error("SUPABASE_SECRET_KEYS illeggibile:", String(e).slice(0, 120));
  }
  return Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? null;
}

function risposta(corpo: unknown, stato = 200): Response {
  return new Response(JSON.stringify(corpo), {
    status: stato,
    headers: { ...CORS, "Content-Type": "application/json" },
  });
}

function pulisci(s: string): string {
  return s.replace(/[<>&]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[c]!));
}

/** Chiama l'archivio con i panni del server. */
async function archivio(rpc: string, corpo: unknown, chiave: string) {
  const r = await fetch(`${Deno.env.get("SUPABASE_URL")}/rest/v1/rpc/${rpc}`, {
    method: "POST",
    headers: {
      apikey: chiave,
      Authorization: `Bearer ${chiave}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(corpo),
  });
  if (!r.ok) {
    const dettaglio = (await r.text()).slice(0, 160);
    console.error(`${rpc}:`, r.status, dettaglio);
    return { errore: { stato: r.status, dettaglio } };
  }
  return { dati: await r.json() };
}

/** Manda una mail con Brevo. Torna null se e' andata, altrimenti il motivo. */
async function posta(a: string, oggetto: string, html: string): Promise<string | null> {
  if (!CHIAVE_BREVO) {
    console.error("manca il segreto della chiave Brevo");
    return "posta_non_configurata";
  }
  const m = await fetch("https://api.brevo.com/v3/smtp/email", {
    method: "POST",
    headers: { "api-key": CHIAVE_BREVO, "Content-Type": "application/json" },
    body: JSON.stringify({
      sender: { name: MITTENTE_NOME, email: MITTENTE_EMAIL },
      replyTo: { name: MITTENTE_NOME, email: RISPONDI_A },
      to: [{ email: a }],
      subject: oggetto,
      htmlContent: html,
    }),
  });
  if (!m.ok) {
    console.error("brevo:", m.status, (await m.text()).slice(0, 200));
    return "posta_non_partita";
  }
  return null;
}

function corpoMail(temi: string[], altro: string | null, link: string): string {
  const elenco = temi.length
    ? `<ul>${temi.map((t) => `<li>${TEMI[t] ?? t}</li>`).join("")}</ul>`
    : "";
  const frase = altro
    ? `<p>${temi.length ? "E hai scritto:" : "Hai scritto:"}</p><blockquote style="margin:0 0 16px;padding:12px 16px;
         border-left:3px solid #e8900a;background:#fff8ee;color:#333">${pulisci(altro)}</blockquote>`
    : "";
  const apertura = temi.length
    ? `<p>Hai segnalato questi temi per gli incontri di settembre di
         Partecipazione Attiva:</p>${elenco}`
    : "";
  return `<div style="font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
       max-width:520px;margin:0 auto;color:#222;line-height:1.6">
  <p style="font-size:1.05em"><b>Manca solo un clic.</b></p>
  ${apertura}${frase}
  <p>Per far contare la tua risposta conferma che questo indirizzo &egrave; tuo:</p>
  <p style="margin:26px 0">
    <a href="${link}" style="background:#e8900a;color:#2b1a00;padding:14px 30px;
       border-radius:50px;text-decoration:none;font-weight:700;display:inline-block">
       Conferma la mia risposta</a>
  </p>
  <p style="font-size:.9em;color:#555">Se il pulsante non funziona, copia
     questo indirizzo nel browser:<br><span style="word-break:break-all">${link}</span></p>
  <hr style="border:0;border-top:1px solid #eee;margin:26px 0">
  <p style="font-size:.85em;color:#555">
     <b>Il tuo indirizzo non lo conserviamo.</b> Serve solo a contare una volta
     sola: appena confermi, viene cancellato e al suo posto resta un codice
     illeggibile che non si pu&ograve; ricondurre a nessuno.<br>
     Se non hai chiesto tu questo voto, ignora la mail: senza il clic non
     succede niente, e fra 48 ore sparisce tutto.</p>
  <p style="font-size:.85em;color:#555">Partecipazione Attiva &mdash;
     <a href="${SITO}">partecipazione-attiva.it</a></p>
</div>`;
}

function corpoAvviso(testo: string, temi: string[]): string {
  const elenco = temi.length
    ? `<p style="color:#555;font-size:.9em">Aveva segnato anche:
       ${temi.map((t) => TEMI[t] ?? t).join(" &middot; ")}</p>`
    : `<p style="color:#555;font-size:.9em">Non ha segnato nessuno dei sei temi:
       ha scritto soltanto questo.</p>`;
  return `<div style="font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
       max-width:560px;margin:0 auto;color:#222;line-height:1.6">
  <p><b>Qualcuno ha scritto cosa ha a cuore</b>, nel sondaggio di settembre.</p>
  <blockquote style="margin:18px 0;padding:16px 18px;border-left:4px solid #e8900a;
       background:#fff8ee;font-size:1.05em">${pulisci(testo)}</blockquote>
  ${elenco}
  <hr style="border:0;border-top:1px solid #eee;margin:22px 0">
  <p style="font-size:.85em;color:#555">
     &Egrave; <b>anonima</b>: l'indirizzo di chi l'ha scritta &egrave; gi&agrave; stato cancellato e
     non &egrave; recuperabile. Non si pu&ograve; rispondere a questa persona.<br>
     La frase &egrave; conservata anche nel pannello, in <i>sondaggio_proposte</i>.<br>
     <b>Non &egrave; stata pubblicata da nessuna parte:</b> decidete voi se e come usarla.</p>
</div>`;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return risposta({ ok: false, motivo: "metodo" }, 405);

  let dati: Record<string, unknown>;
  try {
    dati = await req.json();
  } catch {
    return risposta({ ok: false, motivo: "richiesta_illeggibile" }, 400);
  }

  const CHIAVE_SERVER = chiaveDelServer();
  if (!CHIAVE_SERVER) {
    console.error("nessuna chiave server disponibile");
    return risposta({ ok: false, motivo: "archivio", stato: 0 }, 500);
  }

  // ---------------------------------------------------------------- CONFERMA
  if (dati.azione === "conferma") {
    const token = String(dati.t ?? "");
    if (!/^[0-9a-f-]{36}$/i.test(token)) {
      return risposta({ esito: "scaduto" });
    }
    const r = await archivio("sondaggio_conferma", { p_token: token }, CHIAVE_SERVER);
    if (r.errore) return risposta({ esito: "errore", ...r.errore }, 500);
    const e = r.dati;

    // se ha scritto qualcosa, la giro al movimento. Se la posta non parte,
    // il voto resta comunque contato: la frase e' salvata nell'archivio.
    if (e?.esito === "contato" && e?.proposta) {
      const guaio = await posta(
        AVVISI_A,
        "Sondaggio settembre: qualcuno ha scritto cosa ha a cuore",
        corpoAvviso(String(e.proposta), Array.isArray(e.scelti) ? e.scelti : []),
      );
      if (guaio) console.error("avviso al movimento non partito:", guaio);
    }

    // al sito NON torna mai il testo scritto dalla persona
    return risposta({
      esito: e?.esito,
      risultati: e?.risultati ?? null,
      totale: e?.totale ?? 0,
    });
  }

  // ------------------------------------------------------------------- VOTO
  const email = String(dati.email ?? "").trim().toLowerCase();
  const temi = Array.isArray(dati.temi) ? dati.temi.map(String) : [];
  const altro = String(dati.altro ?? "").trim().slice(0, 400);

  if (temi.length > 6 || !temi.every((t) => t in TEMI)) {
    return risposta({ ok: false, motivo: "temi_non_validi" }, 400);
  }
  if (temi.length === 0 && !altro) {
    return risposta({ ok: false, motivo: "temi_non_validi" }, 400);
  }
  if (!/^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(email)) {
    return risposta({ ok: false, motivo: "email_non_valida" }, 400);
  }

  const r = await archivio("sondaggio_registra",
    { p_email: email, p_temi: temi, p_altro: altro || null }, CHIAVE_SERVER);
  if (r.errore) return risposta({ ok: false, motivo: "archivio", ...r.errore }, 500);
  const esito = r.dati;

  if (esito?.esito === "gia_votato") return risposta({ ok: false, motivo: "gia_votato" });
  if (esito?.esito === "gia_inviata") return risposta({ ok: false, motivo: "gia_inviata" });
  if (esito?.esito !== "da_confermare" || !esito?.token) {
    return risposta({ ok: false, motivo: esito?.esito ?? "sconosciuto" }, 400);
  }

  const link = `${SITO}/voto-confermato.html?t=${esito.token}`;
  const guaio = await posta(email, "Conferma il tuo voto sui temi di settembre",
    corpoMail(temi, altro || null, link));
  if (guaio) return risposta({ ok: false, motivo: guaio }, 502);

  // al sito NON dico mai il codice
  return risposta({ ok: true });
});
