#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BANCO DI PROVA — sito Partecipazione Attiva
============================================
Misura sempre le stesse cose, nello stesso ordine, e archivia il risultato con
la data. Serve a non dover mai dire «mi sembra migliorato».

Fase 0 del PIANO_ESECUTIVO_SITO_PA (8 agosto 2026).

    python3 _tools/banco_misura.py                 # misura e archivia
    python3 _tools/banco_misura.py --confronta     # confronta con la volta prima
    python3 _tools/banco_misura.py --sorgente locale   # misura i file su disco

NON MODIFICA NIENTE. Legge e basta.

Due strumenti distinti, come dice il piano:
  - il BANCO campiona 6 pagine con misure vive (pixel, tempi, contrasti)
  - l'AUDIT STATICO (analizza_sito.py) verifica tutte le pagine

Metriche: LCP e CLS sono Core Web Vitals di laboratorio. TBT NON e' un Core Web
Vital: e' la spia diagnostica di INP, che si puo' misurare solo sul campo (utenti
veri) e quindi non entra in questo banco.
"""

import argparse, json, os, re, subprocess, sys, tempfile, shutil
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVIO = os.path.join(REPO, "_audit", "banco")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

BASE_WEB = "https://partecipazione-attiva.it"

# Le sei pagine campione: home + un articolo + le cinque sezioni che contano
CAMPIONE = [
    ("home", "index.html"),
    ("articolo", "cavalleggeri-cielo-aperto.html"),
    ("mappa", "mappa.html"),
    ("battaglie", "battaglie.html"),
    ("territori", "territori.html"),
    ("webtv", "webtv.html"),
]

LARGHEZZE = [320, 375, 390, 414, 768, 1280]

# --------------------------------------------------------------------------
# Il pezzo di JavaScript che fa le misure dentro la pagina.
# Sta qui in un pezzo solo perche' deve restare identico a ogni esecuzione:
# se cambia il metro, i confronti non valgono piu'.
# --------------------------------------------------------------------------
MISURA_JS = r"""
(() => {
  const R = {};
  const de = document.documentElement;
  R.larghezza_finestra = de.clientWidth;
  R.altezza_finestra = de.clientHeight;

  // 1. sfondamento orizzontale
  R.larghezza_contenuto = de.scrollWidth;
  R.sfondamento_px = Math.max(0, de.scrollWidth - de.clientWidth);

  // 2. a che altezza compare l'identita' (il primo H1)
  const h1 = document.querySelector('h1');
  R.identita_px = h1 ? Math.round(h1.getBoundingClientRect().top + window.scrollY) : null;
  R.identita_testo = h1 ? h1.textContent.trim().replace(/\s+/g, ' ').slice(0, 60) : null;

  // 3. intestazione
  const nav = document.querySelector('nav.navbar, nav#navbar, nav');
  R.intestazione_px = nav ? Math.round(nav.getBoundingClientRect().height) : null;
  const voci = nav ? [...nav.querySelectorAll('a')] : [];
  const visibili = voci.filter(a => a.getBoundingClientRect().width > 0);
  R.voci_menu = visibili.length;
  const righe = new Set(visibili.map(a => Math.round(a.getBoundingClientRect().top / 5)));
  R.righe_menu = righe.size;

  // 4. bersagli da toccare troppo piccoli (soglia 44px, norma WCAG 2.2 AAA;
  //    24px e' il minimo AA. Contiamo entrambi.)
  let sotto24 = 0, sotto44 = 0;
  document.querySelectorAll('a,button,input,select,[role=button]').forEach(e => {
    const r = e.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return;
    const s = getComputedStyle(e);
    if (s.visibility === 'hidden' || s.display === 'none') return;
    if (r.height < 24 || r.width < 24) sotto24++;
    if (r.height < 44) sotto44++;
  });
  R.bersagli_sotto_24 = sotto24;
  R.bersagli_sotto_44 = sotto44;

  // 5. struttura per chi non usa il mouse
  R.ha_main = !!document.querySelector('main');
  R.ha_salta_al_contenuto = !!document.querySelector(
    'a[href="#contenuto"],a[href="#main"],a[href="#principale"],a.skip-link,a[class*="salta"]');

  // 6. immagini
  const imgs = [...document.images];
  R.immagini = imgs.length;
  R.immagini_senza_alt = imgs.filter(i => !i.hasAttribute('alt')).length;
  R.immagini_senza_dimensioni = imgs.filter(i => !i.getAttribute('width') || !i.getAttribute('height')).length;

  // 7. risorse e domini esterni realmente CARICATI (non i link cliccabili)
  const res = performance.getEntriesByType('resource');
  R.richieste = res.length;
  R.file_carattere = res.filter(r => /\.woff2?($|\?)/.test(r.name)).length;
  const host = location.hostname;
  R.domini_esterni = [...new Set(res.map(r => { try { return new URL(r.name).hostname; } catch (e) { return null; } })
    .filter(h => h && h !== host))].sort();

  // 8. tempi (indicativi: la verita' sta nei dati di campo)
  const nav0 = performance.getEntriesByType('navigation')[0];
  R.dom_pronto_ms = nav0 ? Math.round(nav0.domContentLoadedEventEnd) : null;

  // 9. contrasti: SOLO dove lo sfondo e' opaco.
  //    Se si risale al primo sfondo non trasparente si prendono i veli
  //    semitrasparenti e si producono falsi positivi in massa (81 presunti,
  //    1 vero, prova dell'8 agosto 2026). Meglio contare meno e giusto.
  const lum = c => {
    const m = (c.match(/[\d.]+/g) || []).map(Number);
    if (m.length < 3) return null;
    const f = m.slice(0, 3).map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
    return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2];
  };
  const opaco = c => c && !/rgba\(.*,\s*(0|0?\.\d+)\)\s*$/.test(c) && !c.includes('rgba(0, 0, 0, 0)');
  const sfondoOpaco = e => {
    let n = e;
    while (n && n !== document.documentElement) {
      const c = getComputedStyle(n).backgroundColor;
      if (c && !c.includes('rgba(0, 0, 0, 0)')) return opaco(c) ? c : null; // velo => rinuncio
      n = n.parentElement;
    }
    return 'rgb(255, 255, 255)';
  };
  const bassi = [];
  let esaminati = 0, saltati = 0;
  document.querySelectorAll('a,button,p,li,span,h1,h2,h3,h4,h5,h6,td,th,label').forEach(e => {
    const t = [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join('');
    if (!t || t.length < 3) return;
    const r = e.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return;
    const s = getComputedStyle(e);
    if (s.visibility === 'hidden' || parseFloat(s.opacity) < 0.5) return;
    const bg = sfondoOpaco(e);
    if (!bg) { saltati++; return; }          // sfondo non determinabile: NON conto
    const L1 = lum(s.color), L2 = lum(bg);
    if (L1 === null || L2 === null) { saltati++; return; }
    esaminati++;
    const cr = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const fs = parseFloat(s.fontSize), grassetto = parseInt(s.fontWeight) >= 700;
    const soglia = (fs >= 24 || (fs >= 18.66 && grassetto)) ? 3 : 4.5;
    if (cr < soglia) bassi.push({ testo: t.slice(0, 40), rapporto: +cr.toFixed(2), soglia, colore: s.color, sfondo: bg });
  });
  R.contrasti_esaminati = esaminati;
  R.contrasti_non_determinabili = saltati;
  R.contrasti_bassi = bassi.length;
  R.contrasti_dettaglio = bassi.slice(0, 10);

  return R;
})()
"""


def _chrome(url, larghezza, altezza=900, extra=None):
    """Esegue MISURA_JS dentro la pagina e restituisce il dizionario."""
    with tempfile.TemporaryDirectory() as tmp:
        script = os.path.join(tmp, "m.js")
        open(script, "w").write(MISURA_JS)
        cmd = [
            CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--no-first-run", "--no-default-browser-check",
            f"--user-data-dir={tmp}/prof",
            f"--window-size={larghezza},{altezza}",
            "--virtual-time-budget=9000",
            "--dump-dom",  # segnaposto, sostituito sotto
            url,
        ]
        # Chrome headless non esegue JS arbitrario da riga di comando: usiamo
        # il protocollo di debug tramite una pagina ponte.
        return None  # sostituito da _via_cdp


def _via_cdp(url, larghezza, altezza=900):
    """Misura usando il protocollo di debug di Chrome (nessuna dipendenza esterna)."""
    import http.client, urllib.request, socket, time, json as _j, threading, base64
    with tempfile.TemporaryDirectory() as tmp:
        porta = _porta_libera()
        proc = subprocess.Popen(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--no-first-run", "--no-default-browser-check",
             f"--remote-debugging-port={porta}", f"--user-data-dir={tmp}",
             f"--window-size={larghezza},{altezza}", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            ws = _attendi_ws(porta)
            if not ws:
                return {"errore": "chrome non risponde"}
            return _cdp_valuta(ws, url, larghezza, altezza)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()


def _porta_libera():
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def _attendi_ws(porta, secondi=15):
    import urllib.request, time, json as _j
    for _ in range(secondi * 5):
        try:
            d = _j.load(urllib.request.urlopen(f"http://127.0.0.1:{porta}/json", timeout=1))
            for t in d:
                if t.get("type") == "page":
                    return t["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(0.2)
    return None


def _cdp_valuta(ws_url, url, larghezza, altezza):
    """Parla col browser via WebSocket, senza librerie esterne."""
    import socket, base64, os as _os, struct, json as _j, time
    from urllib.parse import urlparse
    u = urlparse(ws_url)
    s = socket.create_connection((u.hostname, u.port), timeout=30)
    key = base64.b64encode(_os.urandom(16)).decode()
    s.sendall((f"GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\n"
               f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        buf += s.recv(4096)

    def invia(msg):
        d = _j.dumps(msg).encode()
        h = b"\x81"
        n = len(d)
        mask = _os.urandom(4)
        if n < 126:
            h += bytes([0x80 | n])
        elif n < 65536:
            h += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            h += bytes([0x80 | 127]) + struct.pack(">Q", n)
        s.sendall(h + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(d)))

    def ricevi():
        def leggi(n):
            b = b""
            while len(b) < n:
                p = s.recv(n - len(b))
                if not p:
                    raise IOError("connessione chiusa")
                b += p
            return b
        h = leggi(2)
        n = h[1] & 127
        if n == 126:
            n = struct.unpack(">H", leggi(2))[0]
        elif n == 127:
            n = struct.unpack(">Q", leggi(8))[0]
        return _j.loads(leggi(n).decode())

    idc = [0]

    def cmd(metodo, params=None, attendi=True):
        idc[0] += 1
        i = idc[0]
        invia({"id": i, "method": metodo, "params": params or {}})
        if not attendi:
            return None
        for _ in range(500):
            m = ricevi()
            if m.get("id") == i:
                return m
        return None

    try:
        cmd("Page.enable")
        cmd("Runtime.enable")
        cmd("Emulation.setDeviceMetricsOverride", {
            "width": larghezza, "height": altezza, "deviceScaleFactor": 1,
            "mobile": larghezza < 768})
        cmd("Page.navigate", {"url": url})
        time.sleep(6)  # lasciamo caricare tutto, comprese le immagini pigre
        r = cmd("Runtime.evaluate", {
            "expression": MISURA_JS, "returnByValue": True, "awaitPromise": False})
        val = ((r or {}).get("result", {}).get("result", {}) or {}).get("value")
        if val is None:
            ecc = (r or {}).get("result", {}).get("exceptionDetails")
            return {"errore": str(ecc)[:200] if ecc else "nessun valore"}
        # errori in console
        return val
    finally:
        s.close()


def misura(sorgente="web"):
    ris = {
        "quando": datetime.now().isoformat(timespec="seconds"),
        "sorgente": sorgente,
        "pagine": {},
    }
    for nome, file in CAMPIONE:
        percorso = os.path.join(REPO, file)
        # Controllo che la pagina campione ESISTA. Senza questo si finisce a
        # misurare la pagina 404 credendo di misurare un articolo: successo
        # davvero, l'8 agosto 2026, al primo collaudo del banco.
        if not os.path.exists(percorso):
            print(f"  ❌ {file} NON ESISTE nel repository — campione saltato")
            print(f"     (senza questo controllo si misurerebbe la pagina 404)")
            ris.setdefault("campioni_mancanti", []).append(file)
            continue
        url = ("file://" + percorso) if sorgente == "locale" else f"{BASE_WEB}/{file}"
        ris["pagine"][nome] = {}
        for larghezza in ([375, 1280] if nome != "home" else LARGHEZZE):
            print(f"  📏 {nome:10} a {larghezza:5} px …", end="", flush=True)
            m = _via_cdp(url, larghezza)
            ris["pagine"][nome][str(larghezza)] = m
            if "errore" in m:
                print(f" ❌ {m['errore'][:50]}")
            else:
                print(f" identità {m.get('identita_px')} px · sfondamento {m.get('sfondamento_px')} px")
    return ris


def salva(ris):
    os.makedirs(ARCHIVIO, exist_ok=True)
    stamp = ris["quando"].replace(":", "").replace("-", "")
    p = os.path.join(ARCHIVIO, f"banco_{stamp}.json")
    json.dump(ris, open(p, "w"), ensure_ascii=False, indent=1)
    return p


def riepilogo(ris):
    print("\n" + "=" * 62)
    print("  BANCO DI PROVA —", ris["quando"], f"({ris['sorgente']})")
    print("=" * 62)
    h = ris["pagine"].get("home", {})
    tel = h.get("375", {})
    des = h.get("1280", {})
    if tel and "errore" not in tel:
        print(f"  Identità visibile dopo         {tel.get('identita_px')} px  (telefono)")
        print(f"  Sfondamento orizzontale        {tel.get('sfondamento_px')} px")
        print(f"  Bersagli sotto 44 px           {tel.get('bersagli_sotto_44')}  (sotto 24: {tel.get('bersagli_sotto_24')})")
    if des and "errore" not in des:
        print(f"  Voci di menu                   {des.get('voci_menu')} su {des.get('righe_menu')} righe")
        print(f"  Altezza intestazione           {des.get('intestazione_px')} px")
        print(f"  File di carattere              {des.get('file_carattere')}")
        print(f"  Richieste                      {des.get('richieste')}")
        print(f"  Domini esterni caricati        {len(des.get('domini_esterni', []))}  {des.get('domini_esterni')}")
        print(f"  Contrasti bassi (certi)        {des.get('contrasti_bassi')}   "
              f"[esaminati {des.get('contrasti_esaminati')}, non determinabili {des.get('contrasti_non_determinabili')}]")
    print("\n  Pagine campione — struttura per chi non usa il mouse:")
    for nome in ris["pagine"]:
        d = ris["pagine"][nome].get("1280") or ris["pagine"][nome].get("375") or {}
        if "errore" in d:
            continue
        print(f"    {nome:10}  <main>: {'sì' if d.get('ha_main') else 'NO':3}   "
              f"salta-al-contenuto: {'sì' if d.get('ha_salta_al_contenuto') else 'NO':3}   "
              f"img senza alt: {d.get('immagini_senza_alt')}")
    print("\n  Sfondamento su tutte le larghezze (home):")
    for L in LARGHEZZE:
        d = h.get(str(L), {})
        if "errore" not in d and d:
            v = d.get("sfondamento_px")
            print(f"    {L:5} px → {v:3} px {'✅' if v == 0 else '❌'}")
    print("=" * 62)


def confronta():
    if not os.path.isdir(ARCHIVIO):
        print("Nessuna misura archiviata.")
        return
    f = sorted(os.listdir(ARCHIVIO))
    f = [x for x in f if x.endswith(".json")]
    if len(f) < 2:
        print("Serve almeno una misura precedente per confrontare.")
        return
    a = json.load(open(os.path.join(ARCHIVIO, f[-2])))
    b = json.load(open(os.path.join(ARCHIVIO, f[-1])))
    print(f"\nCONFRONTO  {a['quando']}  →  {b['quando']}\n")
    chiavi = ["identita_px", "sfondamento_px", "bersagli_sotto_44", "voci_menu",
              "righe_menu", "intestazione_px", "file_carattere", "richieste",
              "contrasti_bassi", "immagini_senza_alt"]
    for L in ["375", "1280"]:
        va, vb = a["pagine"].get("home", {}).get(L, {}), b["pagine"].get("home", {}).get(L, {})
        if not va or not vb or "errore" in va or "errore" in vb:
            continue
        print(f"  home a {L} px:")
        for k in chiavi:
            x, y = va.get(k), vb.get(k)
            if x is None and y is None:
                continue
            segno = "=" if x == y else ("↓" if (isinstance(x, int) and isinstance(y, int) and y < x) else "↑")
            marca = "" if x == y else ("  ✅" if segno == "↓" else "  ⚠️")
            print(f"    {k:24} {str(x):>6} → {str(y):>6}  {segno}{marca}")
        print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Banco di prova del sito PA — legge e basta, non modifica niente")
    ap.add_argument("--sorgente", choices=["web", "locale"], default="web")
    ap.add_argument("--confronta", action="store_true")
    a = ap.parse_args()
    if a.confronta:
        confronta()
        sys.exit(0)
    if not os.path.exists(CHROME):
        print("❌ Google Chrome non trovato:", CHROME)
        sys.exit(1)
    print(f"🔬 Banco di prova — sorgente: {a.sorgente}\n")
    r = misura(a.sorgente)
    p = salva(r)
    riepilogo(r)
    print(f"\n  archiviato in: {p}")
