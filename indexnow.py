import urllib.request, json

KEY = "4bb4591fa00166eacb3cfeccea85e890"
HOST = "partecipazioneattiva.github.io"
PAGES = [
    "index.html","battaglie.html","rcauto.html","sanitapubblica.html",
    "stabilicum.html","napoli.html","parlero.html","territori.html",
    "organigramma.html","privacy.html","spanu-sire.html",
    "spanu-stabilicum.html","astensionismo.html"
]

payload = json.dumps({
    "host": HOST,
    "key": KEY,
    "keyLocation": f"https://{HOST}/{KEY}.txt",
    "urlList": [f"https://{HOST}/{p}" for p in PAGES]
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.indexnow.org/indexnow",
    data=payload,
    headers={"Content-Type":"application/json"},
    method="POST"
)
try:
    resp = urllib.request.urlopen(req)
    print(f"Inviate {len(PAGES)} URL a IndexNow")
    print(f"Risposta: {resp.status} {resp.reason}")
except urllib.error.HTTPError as e:
    print(f"Errore: {e.code} {e.reason}")
