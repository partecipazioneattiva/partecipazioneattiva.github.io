// =====================================================================
// FUNZIONE "sondaggio" - Partecipazione Attiva - 9 agosto 2026
// =====================================================================
// Si installa in Supabase come Edge Function di nome esattamente:
//     sondaggio
//
// COSA FA, in ordine:
//   1. controlla che i temi siano fra i sei (scelta multipla libera) e che
//      ci sia almeno un tema OPPURE una frase scritta a mano;
//   2. passa tutto all'archivio, che rimescola l'indirizzo col segreto e
//      CONTA SUBITO il voto. L'indirizzo in chiaro non viene conservato
//      da nessuna parte, nemmeno per un istante;
//   3. se la persona ha scritto qualcosa nella casella "altro", manda
//      quella frase AL MOVIMENTO per posta. E' l'unico modo in cui una
//      frase esce dall'archivio: al sito non torna mai;
//   4. risponde al sito con i numeri aggiornati, cosi' chi ha appena
//      votato vede subito come sta andando.
//
// NIENTE MAIL DI CONFERMA A CHI VOTA. Nelle prime ore due persone hanno
// votato davvero, le mail sono state consegnate, e nessuna delle due ha
// cliccato: quel passaggio non proteggeva, perdeva voti. Il sondaggio e'
// INDICATIVO - dice dove va l'interesse, non proclama un vincitore.
//
// !! NIENTE LETTERE ACCENTATE IN QUESTO FILE. L'editor di Supabase le
// rovina quando si incolla: si usano le forme HTML (&egrave; &rsquo;).
//
// NON contiene chiavi. Le legge dai segreti del progetto.
// =====================================================================

const SITO = "https://partecipazione-attiva.it";

// A chi arrivano le frasi scritte nella casella "altro".
const AVVISI_A = Deno.env.get("SONDAGGIO_AVVISI_A") ??
  "webmaster.partecipazione.attiva@gmail.com";

// IL MITTENTE. Trappola gia' pagata: sulle mail spedite Gmail mostra un
// indirizzo @NUMERO.brevosend.com, ma quello NON e' il mittente da
// dichiarare - e' quello che Brevo ci mette al posto suo. Va dichiarato
// l'indirizzo VERO, quello validato nell'account Brevo.
const MITTENTE_EMAIL =
  Deno.env.get("BREVO_MITTENTE") ??
  "webmaster.partecipazione.attiva@gmail.com";
const MITTENTE_NOME = "Partecipazione Attiva";

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
 * Dal 2026 Supabase ha cambiato sistema: SUPABASE_SERVICE_ROLE_KEY e'
 * dichiarata obsoleta, al suo posto c'e' SUPABASE_SECRET_KEYS, che NON e'
 * una stringa ma un elenco JSON da cui si prende la voce 'default'.
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
     &Egrave; <b>anonima</b>: l&rsquo;indirizzo di chi l&rsquo;ha scritta non &egrave; mai
     stato conservato, quindi non &egrave; recuperabile. Non si pu&ograve; rispondere a
     questa persona.<br>
     La frase &egrave; conservata anche nel pannello, in <i>sondaggio_proposte</i>.<br>
     <b>Non &egrave; stata pubblicata da nessuna parte:</b> decidete voi se e come usarla.</p>
  <p style="font-size:.85em;color:#555">Partecipazione Attiva &mdash;
     <a href="${SITO}">partecipazione-attiva.it</a></p>
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

  const email = String(dati.email ?? "").trim().toLowerCase();
  const temi = Array.isArray(dati.temi) ? dati.temi.map(String) : [];
  const altro = String(dati.altro ?? "").trim().slice(0, 400);
  // la prima scelta e' FACOLTATIVA: chi la salta non deve perdere il voto
  // sui temi. Se c'e', dev'essere uno dei sei e uno di quelli segnati.
  const primo = String(dati.primo ?? "").trim();

  if (temi.length > 6 || !temi.every((t) => t in TEMI)) {
    return risposta({ ok: false, motivo: "temi_non_validi" }, 400);
  }
  if (primo && (!(primo in TEMI) || !temi.includes(primo))) {
    return risposta({ ok: false, motivo: "primo_non_valido" }, 400);
  }
  if (temi.length === 0 && !altro) {
    return risposta({ ok: false, motivo: "temi_non_validi" }, 400);
  }
  if (!/^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(email)) {
    return risposta({ ok: false, motivo: "email_non_valida" }, 400);
  }

  const CHIAVE_SERVER = chiaveDelServer();
  if (!CHIAVE_SERVER) {
    console.error("nessuna chiave server disponibile");
    return risposta({ ok: false, motivo: "archivio", stato: 0 }, 500);
  }

  const r = await fetch(`${Deno.env.get("SUPABASE_URL")}/rest/v1/rpc/sondaggio_vota`, {
    method: "POST",
    headers: {
      apikey: CHIAVE_SERVER,
      Authorization: `Bearer ${CHIAVE_SERVER}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ p_email: email, p_temi: temi, p_altro: altro || null,
                           p_primo: primo || null }),
  });
  if (!r.ok) {
    const dettaglio = (await r.text()).slice(0, 160);
    console.error("vota:", r.status, dettaglio);
    return risposta({ ok: false, motivo: "archivio", stato: r.status, dettaglio }, 500);
  }
  const e = await r.json();

  if (e?.esito === "gia_votato") return risposta({ ok: false, motivo: "gia_votato" });
  if (e?.esito !== "contato") {
    return risposta({ ok: false, motivo: e?.esito ?? "sconosciuto" }, 400);
  }

  // se ha scritto qualcosa, la giro al movimento. Se la posta non parte il
  // voto resta comunque contato: la frase e' gia' salvata nell'archivio.
  if (e?.proposta) {
    const guaio = await posta(
      AVVISI_A,
      "Sondaggio settembre: qualcuno ha scritto cosa ha a cuore",
      corpoAvviso(String(e.proposta), temi),
    );
    if (guaio) console.error("avviso al movimento non partito:", guaio);
  }

  // al sito NON torna mai il testo scritto dalla persona
  return risposta({
    ok: true,
    risultati: e?.risultati ?? null,
    persone: e?.persone ?? 0,
  });
});
