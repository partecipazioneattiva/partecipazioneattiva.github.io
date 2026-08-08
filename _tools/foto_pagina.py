#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOTO DI UNA PAGINA — come la vede DAVVERO un telefono
======================================================
    python3 _tools/foto_pagina.py index.html 375
    python3 _tools/foto_pagina.py https://partecipazione-attiva.it/ 375 --intera

⚠️  PERCHE' ESISTE QUESTO STRUMENTO
Chrome con "--window-size=375" NON simula un telefono: ignora le regole del
viewport, disegna la pagina piu' larga e poi ritaglia. Il risultato sembra un
sito con i testi tagliati a destra. E' un inganno dello strumento, non un
difetto del sito — ci sono cascato due volte l'8 agosto 2026, la prima
credendo che il sito fosse rotto a meta' sul telefono, la seconda credendo che
il titolo nuovo della home fosse tagliato.

Questo strumento usa invece l'emulazione vera (Emulation.setDeviceMetricsOverride
via protocollo di debug), la stessa che usa il banco di misura. Quello che si
vede qui e' quello che vede il telefono.
"""
import base64, json, os, socket, struct, subprocess, sys, tempfile, time
from urllib.parse import urlparse

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _porta_libera():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def _ws(porta, secondi=15):
    import urllib.request
    for _ in range(secondi * 5):
        try:
            for t in json.load(urllib.request.urlopen(f"http://127.0.0.1:{porta}/json", timeout=1)):
                if t.get("type") == "page":
                    return t["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(0.2)
    return None


def foto(url, larghezza, altezza=812, intera=False, dpr=2):
    with tempfile.TemporaryDirectory() as tmp:
        porta = _porta_libera()
        proc = subprocess.Popen(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--no-first-run", "--no-default-browser-check",
             f"--remote-debugging-port={porta}", f"--user-data-dir={tmp}", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            w = _ws(porta)
            if not w:
                return None
            u = urlparse(w)
            s = socket.create_connection((u.hostname, u.port), timeout=60)
            key = base64.b64encode(os.urandom(16)).decode()
            s.sendall((f"GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\n"
                       f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
                       f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
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
                out = b""
                while len(out) < n:
                    p = s.recv(n - len(out))
                    if not p:
                        raise IOError("chiuso")
                    out += p
                return out

            def ricevi():
                h = leggi(2); n = h[1] & 127
                if n == 126: n = struct.unpack(">H", leggi(2))[0]
                elif n == 127: n = struct.unpack(">Q", leggi(8))[0]
                return json.loads(leggi(n).decode())

            idc = [0]

            def cmd(metodo, params=None):
                idc[0] += 1; i = idc[0]
                invia({"id": i, "method": metodo, "params": params or {}})
                for _ in range(800):
                    m = ricevi()
                    if m.get("id") == i:
                        return m
                return None

            cmd("Page.enable")
            # ⬇️ QUESTA e' la riga che fa la differenza: emulazione telefono vera
            cmd("Emulation.setDeviceMetricsOverride", {
                "width": larghezza, "height": altezza, "deviceScaleFactor": dpr,
                "mobile": larghezza < 768,
                "screenWidth": larghezza, "screenHeight": altezza})
            cmd("Page.navigate", {"url": url})
            time.sleep(6)
            if intera:
                r = cmd("Page.getLayoutMetrics")
                h = int(((r or {}).get("result", {}).get("cssContentSize", {}) or {}).get("height", altezza))
                cmd("Emulation.setDeviceMetricsOverride", {
                    "width": larghezza, "height": min(h, 16000), "deviceScaleFactor": dpr,
                    "mobile": larghezza < 768})
                time.sleep(2)
            r = cmd("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": intera})
            dati = ((r or {}).get("result", {}) or {}).get("data")
            return base64.b64decode(dati) if dati else None
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    arg = sys.argv[1]
    larghezza = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 375
    intera = "--intera" in sys.argv
    url = arg if arg.startswith("http") else "file://" + os.path.join(REPO, arg)
    png = foto(url, larghezza, intera=intera)
    if not png:
        print("❌ non sono riuscito a fotografare"); sys.exit(1)
    nome = f"foto_{os.path.basename(arg).split('.')[0] or 'pagina'}_{larghezza}.png"
    open(nome, "wb").write(png)
    print(f"✅ {nome}  ({len(png)//1024} KB)")
