#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHI SBORDA — trova CHI fa scorrere la pagina di lato, non chi ne subisce l'effetto
==================================================================================
9 agosto 2026.

    python3 _tools/chi_sborda.py                    # tutte le pagine, 320/375/414
    python3 _tools/chi_sborda.py ape.html 320       # una pagina, una larghezza

⚠️ IL PRINCIPIO, ed e' l'unica cosa importante di questo file:

    IL COLPEVOLE E' L'ELEMENTO CHE ESCE DALLO SCHERMO MENTRE SUO PADRE NON ESCE.

Se un contenitore sborda, sbordano anche TUTTI i suoi figli: una pagina rotta
ne segnala trenta, e ventinove sono vittime. Cercando «gli elementi che escono»
si trova una folla; guardando il piu' profondo si trova quasi sempre un
innocente. Guardando invece chi esce mentre suo padre sta dentro, il colpevole
e' uno solo e salta fuori subito.

Il 9 agosto 2026 questo e' costato un'ora: cercavo elemento per elemento e ne
spuntava sempre un altro. Poi ho letto come lo risolvono gli esperti — Ahmad
Shadeed, «Overflow Issues In CSS», Smashing Magazine — e in cinque minuti erano
sistemate cinque pagine.

Due accorgimenti che evitano falsi allarmi:
  · si saltano gli elementi dentro un contenitore che li RITAGLIA (overflow
    auto/hidden/scroll/clip): sono nascosti, non sbordano davvero. E' il caso
    delle tabelle dentro un riquadro che scorre;
  · si segnala a parte cio' che e' `position: fixed` (bottoni galleggianti,
    riquadri delle notifiche): quelli si ancorano allo schermo e spesso sono
    la CONSEGUENZA di una pagina gia' larga, non la causa.

LE CAUSE VERE SONO UN ELENCO CHIUSO (fonte: Shadeed, Smashing Magazine):
  1. misure fisse in px piu' larghe dello schermo   -> min(400px, 100%)
  2. parole o indirizzi non spezzabili              -> overflow-wrap: break-word
  3. righe flessibili che non vanno a capo          -> flex-wrap: wrap
  4. figli di flex che non si restringono           -> min-width: 0
  5. griglie con «1fr»                              -> minmax(0, 1fr)
  6. immagini senza tetto                           -> img { max-width: 100% }
  7. tabelle di dati                                -> in un riquadro che scorre
  8. elementi posizionati fuori                     -> overflow: hidden sul padre
  9. 100vw (comprende la barra di scorrimento)      -> 100% invece di 100vw
"""
import base64, json, os, socket, struct, subprocess, sys, tempfile, time, urllib.request
from urllib.parse import urlparse

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTA_SITO = 8899

JS = r"""(()=>{const W=document.documentElement.clientWidth;
function esce(e){return e.getBoundingClientRect().right>W+1;}
function ritagliato(e){let p=e.parentElement;
  while(p&&p!==document.documentElement){const o=getComputedStyle(p).overflowX;
    if(o==='auto'||o==='hidden'||o==='scroll'||o==='clip')return true;p=p.parentElement;}
  return false;}
const veri=[], ancorati=[];
document.querySelectorAll('body *').forEach(e=>{
  if(!esce(e)||ritagliato(e)) return;
  const p=e.parentElement;
  if(p && p!==document.body && esce(p)) return;      // e' una vittima
  const s=getComputedStyle(e), r=e.getBoundingClientRect();
  const v={tag:e.tagName.toLowerCase(),cls:(e.className||'').toString().slice(0,26),
    w:Math.round(r.width),da:Math.round(r.left),a:Math.round(r.right),
    disp:s.display,wrap:s.flexWrap,cols:s.gridTemplateColumns.slice(0,30),
    minw:s.minWidth,ws:s.whiteSpace,
    t:(e.textContent||'').trim().replace(/\s+/g,' ').slice(0,30)};
  (s.position==='fixed'?ancorati:veri).push(v);});
const H=document.documentElement;
return JSON.stringify({sfora:Math.round(Math.max(0,H.scrollWidth-H.clientWidth)),
  veri:veri, ancorati:ancorati.slice(0,2)});})()"""


def browser():
    tmp = tempfile.mkdtemp()
    s0 = socket.socket(); s0.bind(("127.0.0.1", 0)); porta = s0.getsockname()[1]; s0.close()
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
         "--no-default-browser-check", f"--remote-debugging-port={porta}",
         f"--user-data-dir={tmp}", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    w = None
    for _ in range(75):
        try:
            for t in json.load(urllib.request.urlopen(f"http://127.0.0.1:{porta}/json", timeout=1)):
                if t.get("type") == "page":
                    w = t["webSocketDebuggerUrl"]; break
        except Exception:
            pass
        if w: break
        time.sleep(.2)
    u = urlparse(w); s = socket.create_connection((u.hostname, u.port), timeout=60)
    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall((f"GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\n"
               f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
               f"Sec-WebSocket-Version: 13\r\n\r\n").encode())
    b = b""
    while b"\r\n\r\n" not in b:
        b += s.recv(4096)

    def invia(m):
        d = json.dumps(m).encode(); n = len(d); mask = os.urandom(4)
        h = b"\x81" + (bytes([0x80 | n]) if n < 126 else
                       (bytes([0x80 | 126]) + struct.pack(">H", n)) if n < 65536 else
                       (bytes([0x80 | 127]) + struct.pack(">Q", n)))
        s.sendall(h + mask + bytes(c ^ mask[i % 4] for i, c in enumerate(d)))

    def leggi(n):
        o = b""
        while len(o) < n:
            p = s.recv(n - len(o))
            if not p: raise IOError
            o += p
        return o

    def ricevi():
        h = leggi(2); n = h[1] & 127
        if n == 126: n = struct.unpack(">H", leggi(2))[0]
        elif n == 127: n = struct.unpack(">Q", leggi(8))[0]
        return json.loads(leggi(n).decode())

    idc = [0]

    def cmd(m, p=None):
        idc[0] += 1; i = idc[0]; invia({"id": i, "method": m, "params": p or {}})
        for _ in range(900):
            r = ricevi()
            if r.get("id") == i: return r
    cmd("Page.enable")
    return cmd, proc


def main():
    arg = [a for a in sys.argv[1:] if not a.startswith("-")]
    pagine = ([arg[0]] if arg and arg[0].endswith(".html")
              else [f for f in sorted(os.listdir(REPO))
                    if f.endswith(".html") and not f.startswith("google")])
    larghezze = [int(arg[1])] if len(arg) > 1 else [320, 375, 414]

    cmd, proc = browser()
    guai = 0
    try:
        for L in larghezze:
            cmd("Emulation.setDeviceMetricsOverride", {
                "width": L, "height": 900, "deviceScaleFactor": 2,
                "mobile": True, "screenWidth": L, "screenHeight": 900})
            print(f"\n{'=' * 64}\nA {L} px")
            for f in pagine:
                cmd("Page.navigate", {"url": f"http://127.0.0.1:{PORTA_SITO}/{f}"})
                time.sleep(0.8)
                r = cmd("Runtime.evaluate", {"expression": JS, "returnByValue": True})
                try:
                    m = json.loads(r["result"]["result"]["value"])
                except Exception:
                    continue
                if not m["sfora"]:
                    if len(pagine) == 1: print(f"  ✅ {f}")
                    continue
                guai += 1
                print(f"  ⚠️  {f} — sborda {m['sfora']} px")
                for c in m["veri"]:
                    print(f"      COLPEVOLE  {c['tag']}.{c['cls']}  largo {c['w']} "
                          f"(da {c['da']} a {c['a']})")
                    print(f"                 display={c['disp']} flex-wrap={c['wrap']} "
                          f"min-width={c['minw']} colonne={c['cols']}")
                    print(f"                 «{c['t']}»")
                if not m["veri"] and m["ancorati"]:
                    print("      (solo elementi ancorati allo schermo: di solito e' la")
                    print("       conseguenza di una pagina gia' larga, non la causa)")
    finally:
        proc.terminate()
    print(f"\n{'✅ NESSUNO SBORDO' if not guai else f'⚠️  {guai} casi da guardare'}")


if __name__ == "__main__":
    main()
