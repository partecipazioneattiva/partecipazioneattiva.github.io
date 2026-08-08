// =====================================================================
// FUNZIONE «sondaggio» — riceve un voto e manda la mail di conferma
// Partecipazione Attiva · 8 agosto 2026
// =====================================================================
// Si installa in Supabase come Edge Function di nome esattamente:
//     sondaggio
// (istruzioni passo per passo in LEGGIMI.md, accanto a questo file)
//
// COSA FA, in ordine:
//   1. controlla che i temi siano fra i sei (scelta multipla libera);
//   2. chiede al database di registrare il voto IN ATTESA — e' il
//      database a rimescolare l'indirizzo col segreto, qui non passa;
//   3. manda la mail di conferma con Brevo, lo stesso canale che il sito
//      usa gia' per la Mappa;
//   4. risponde al sito SENZA mai dargli il codice di conferma: se lo
//      desse, chiunque potrebbe confermarsi da solo e la verifica
//      dell'indirizzo non varrebbe niente.
//
// NON contiene chiavi. Le legge dai segreti del progetto.
// =====================================================================

const SITO = "https://partecipazione-attiva.it";

// Il mittente e' quello che il sito usa gia' (visto sulle mail della Mappa).
const MITTENTE_EMAIL =
  Deno.env.get("BREVO_MITTENTE") ??
  "webmaster.partecipazione.attiva@10909356.brevosend.com";
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
  "ape": "APE — l’Assemblea Popolare Ecumenica",
  "mappa": "La Mappa dei cittadini attivi",
  "legge-elettorale": "La legge elettorale",
  "rc-auto": "RC Auto",
  "arte-del-dono": "L’arte del dono",
  "donna-a-napoli": "Essere donna a Napoli",
};

/**
 * LA CHIAVE CON CUI IL SERVER PARLA AL PROPRIO ARCHIVIO.
 *
 * Dal 2026 Supabase ha cambiato sistema di chiavi. Quella vecchia
 * (SUPABASE_SERVICE_ROLE_KEY) e' dichiarata OBSOLETA — nel pannello compare
 * proprio con l'etichetta DEPRECATED — e al suo posto c'e' SUPABASE_SECRET_KEYS,
 * che NON e' una stringa ma un elenco in JSON da cui si prende la voce 'default'.
 *
 * Chiedere solo quella vecchia significa presentarsi all'archivio senza
 * credenziali valide: e' il motivo per cui l'8 agosto 2026 nessuna mail partiva.
 *
 * Qui si prova prima la nuova e poi la vecchia, cosi' funziona sia sui progetti
 * gia' migrati sia su quelli ancora indietro.
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

function corpoMail(temi: string[], link: string): string {
  const elenco = temi.map((t) => `<li>${TEMI[t] ?? t}</li>`).join("");
  return `<div style="font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
       max-width:520px;margin:0 auto;color:#222;line-height:1.6">
  <p style="font-size:1.05em"><b>Manca solo un clic.</b></p>
  <p>Hai scelto questi temi per gli incontri di settembre di
     Partecipazione Attiva:</p>
  <ul>${elenco}</ul>
  <p>Per far contare il tuo voto conferma che questo indirizzo è tuo:</p>
  <p style="margin:26px 0">
    <a href="${link}" style="background:#e8900a;color:#2b1a00;padding:14px 30px;
       border-radius:50px;text-decoration:none;font-weight:700;display:inline-block">
       Conferma il mio voto</a>
  </p>
  <p style="font-size:.9em;color:#555">Se il pulsante non funziona, copia
     questo indirizzo nel browser:<br><span style="word-break:break-all">${link}</span></p>
  <hr style="border:0;border-top:1px solid #eee;margin:26px 0">
  <p style="font-size:.85em;color:#555">
     <b>Il tuo indirizzo non lo conserviamo.</b> Serve solo a contare una volta
     sola: appena confermi, viene cancellato e al suo posto resta un codice
     illeggibile che non si può ricondurre a nessuno.<br>
     Se non hai chiesto tu questo voto, ignora la mail: senza il clic non
     succede niente, e fra 48 ore sparisce tutto.</p>
  <p style="font-size:.85em;color:#555">Partecipazione Attiva —
     <a href="${SITO}">partecipazione-attiva.it</a></p>
</div>`;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return risposta({ ok: false, motivo: "metodo" }, 405);

  let dati: { temi?: unknown; email?: unknown };
  try {
    dati = await req.json();
  } catch {
    return risposta({ ok: false, motivo: "richiesta_illeggibile" }, 400);
  }

  const email = String(dati.email ?? "").trim().toLowerCase();
  const temi = Array.isArray(dati.temi) ? dati.temi.map(String) : [];

  if (temi.length < 1 || temi.length > 6 || !temi.every((t) => t in TEMI)) {
    return risposta({ ok: false, motivo: "temi_non_validi" }, 400);
  }
  if (!/^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(email)) {
    return risposta({ ok: false, motivo: "email_non_valida" }, 400);
  }

  const URL_DB = Deno.env.get("SUPABASE_URL")!;
  const CHIAVE_SERVER = chiaveDelServer();
  if (!CHIAVE_SERVER) {
    console.error("nessuna chiave server disponibile");
    return risposta({ ok: false, motivo: "archivio", stato: 0 }, 500);
  }

  // 1. registro il voto in attesa: e' il database a rimescolare l'indirizzo
  const r = await fetch(`${URL_DB}/rest/v1/rpc/sondaggio_registra`, {
    method: "POST",
    headers: {
      apikey: CHIAVE_SERVER,
      Authorization: `Bearer ${CHIAVE_SERVER}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ p_email: email, p_temi: temi }),
  });
  if (!r.ok) {
    // Il dettaglio torna anche al chiamante: sono messaggi dell'archivio, non
    // contengono chiavi ne' dati di persone, e permettono di capire un guasto
    // dall'esterno senza dover aprire i registri. Si puo' togliere a regime.
    const dettaglio = (await r.text()).slice(0, 160);
    console.error("registra:", r.status, dettaglio);
    return risposta({ ok: false, motivo: "archivio", stato: r.status, dettaglio }, 500);
  }
  const esito = await r.json();

  if (esito?.esito === "gia_votato") {
    return risposta({ ok: false, motivo: "gia_votato" });
  }
  if (esito?.esito === "gia_inviata") {
    return risposta({ ok: false, motivo: "gia_inviata" });
  }
  if (esito?.esito !== "da_confermare" || !esito?.token) {
    return risposta({ ok: false, motivo: esito?.esito ?? "sconosciuto" }, 400);
  }

  // 2. mando la conferma con Brevo
  if (!CHIAVE_BREVO) {
    console.error("manca il segreto della chiave Brevo");
    return risposta({ ok: false, motivo: "posta_non_configurata" }, 500);
  }
  const link = `${SITO}/voto-confermato.html?t=${esito.token}`;
  const m = await fetch("https://api.brevo.com/v3/smtp/email", {
    method: "POST",
    headers: { "api-key": CHIAVE_BREVO, "Content-Type": "application/json" },
    body: JSON.stringify({
      sender: { name: MITTENTE_NOME, email: MITTENTE_EMAIL },
      replyTo: { name: MITTENTE_NOME, email: RISPONDI_A },
      to: [{ email }],
      subject: "Conferma il tuo voto sui temi di settembre",
      htmlContent: corpoMail(temi, link),
    }),
  });
  if (!m.ok) {
    console.error("brevo:", m.status, await m.text());
    return risposta({ ok: false, motivo: "posta_non_partita" }, 502);
  }

  // 3. al sito NON dico mai il codice
  return risposta({ ok: true });
});
