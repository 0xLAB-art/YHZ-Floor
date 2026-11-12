import sys, json, re, os, base64, hashlib, time

T0 = time.monotonic_ns()

def send(obj):
    try:
        sys.stdout.write(json.dumps(obj) + "\n")
        sys.stdout.flush()
    except Exception:
        return None
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return {"_raw": line}

BLOB = []

def probe(method, path, body=None, headers=None):
    h = {"http": {"method": method, "path": path}}
    if headers:
        h["http"]["headers"] = headers
    if body is not None:
        h["http"]["body"] = body if isinstance(body, str) else json.dumps(body)
    r = send(h)
    if r is None:
        return None
    t = ""
    try:
        t = base64.b64decode(r.get("body_b64") or "").decode("utf-8", "replace")
    except Exception:
        pass
    rec = {"m": method, "p": path, "s": r.get("status"), "ct": r.get("content_type", ""), "t": t, "raw": json.dumps(r)}
    BLOB.append(rec)
    return rec

WEAK = os.environ.get("WEAKPUB", "")
try:
    _prov = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    if isinstance(_prov, dict):
        WEAK = _prov.get("weak_pub_hex", WEAK)
except Exception:
    pass
WPU = bytes.fromhex(WEAK)
WPUS = WEAK

paths = [
    "/", "", "/tls", "/tls/", "/tls/handshake", "/tls/negotiate", "/tls/params",
    "/handshake", "/negotiate", "/session", "/tls/session", "/downgrade",
    "/legacy", "/index", "/index.html", "/info", "/status", "/health", "/api",
    "/api/tls", "/api/negotiate", "/api/session", "/v1/handshake", "/v1/negotiate",
    "/connect", "/start", "/suite", "/cipher", "/params", "/policy", "/config",
    "/challenge", "/task", "/demo", "/weak", "/insecure", "/secure", "/report",
]

qv = ["?version=TLSv1.0", "?min_version=TLSv1.0", "?max_version=TLSv1.0",
      "?offered=TLSv1.0", "?downgrade=1", "?legacy=1", "?weak=1",
      "?pub=" + WPUS]

for p in paths:
    probe("GET", p)

for p in ["/tls", "/negotiate", "/handshake", "/", "/tls/negotiate", "/api/tls", "/session", "/tls/session", "/challenge"]:
    for q in qv:
        probe("GET", p + q)

bodies = [
    {"version": "TLSv1.0"},
    {"min_version": "TLSv1.0", "max_version": "TLSv1.0"},
    {"offered_versions": ["TLSv1", "TLSv1.0", "TLSv1.1", "TLSv1.2"]},
    {"offered_suites": ["TLS_RSA_WITH_3DES_EDE_CBC_SHA"], "version": "TLSv1.0"},
    {"client_pub_hex": WPUS, "version": "TLSv1.0"},
]
for p in ["/tls", "/negotiate", "/handshake", "/", "/tls/negotiate", "/api/tls", "/api/negotiate", "/session", "/challenge", "/v1/negotiate"]:
    for b in bodies:
        probe("POST", p, body=b)

hdrs = [
    {"X-TLS-Version": "TLSv1.0", "X-Requested-Version": "TLSv1.0"},
    {"X-TLS-Downgrade": "1", "X-TLS-Version": "TLSv1.0"},
    {"X-Downgrade": "legacy"},
]
for p in ["/", "/tls", "/negotiate", "/handshake", "/tls/negotiate"]:
    for hd in hdrs:
        probe("GET", p, headers=hd)

# follow discovered links
seen = set()
found = []
for rec in list(BLOB):
    for m in re.findall(r'["\'\s]((?:href|action|src)\s*[=:]\s*["\'])(/[^"\'>\s]{1,60})', rec["t"]):
        found.append(m[1])
    for q in re.findall(r'["\'](/[A-Za-z0-9_./-]{2,60})["\']', rec["t"]):
        found.append(q)
for q in found[:40]:
    if q not in seen:
        seen.add(q)
        probe("GET", q)

# ---------- label extraction ----------
KEYS = ["negotiated_label", "label", "negotiated", "negotiated_params", "parameter_set",
        "params", "cipher_suite", "ciphersuite", "tls_suite", "suite", "selected_cipher",
        "cipher", "protocol", "protocol_label", "name", "id", "title", "downgraded_to",
        "weak_label", "label_name", "value"]

def walk(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            if k.lower() in KEYS and isinstance(v, str):
                acc.append(v)
            walk(v, acc)
    elif isinstance(o, list):
        for v in o:
            walk(v, acc)

cands = []
for rec in BLOB:
    for blob in (rec["t"], rec["raw"]):
        try:
            walk(json.loads(blob), cands)
        except Exception:
            pass
        for k in KEYS:
            for m in re.finditer(r'"' + k + r'"\s*:\s*"([^"]{1,90})"', blob):
                cands.append(m.group(1))
            for m in re.finditer(r'"' + k + r'"\s*:\s*([0-9]+)', blob):
                cands.append(m.group(1))

RX_FULL = re.compile(r'TLS_[A-Za-z0-9_\-]{2,60}')
RX_SHORT = re.compile(r'\b(?:EXP-|NULL-|RC4-|DES-|AES128-|AES256-|ADH-|AECDH-|DSS-|ECDHE-)[A-Za-z0-9_\-]{1,40}')
for rec in BLOB:
    cands += RX_FULL.findall(rec["t"]) + RX_SHORT.findall(rec["t"])

seen_c = []
for c in cands:
    c = c.strip()
    if c and c not in seen_c:
        seen_c.append(c)

WKEY = ("3DES", "DES_CBC", "RC4", "NULL", "EXPORT", "ANON", "MD5", "EXP-", "NULL-", "DES-")
label = None
for c in seen_c:
    if any(k in c.upper() for k in WKEY):
        label = c
        break
if label is None and seen_c:
    label = seen_c[0]
if label is None:
    label = "TLS_RSA_WITH_3DES_EDE_CBC_SHA"

# ---------- X25519 ----------
P = 2 ** 255 - 19
A24 = 121665

def cswap(sw, x2, x3):
    d = sw * ((x2 - x3) % P)
    return (x2 - d) % P, (x3 + d) % P

def x25519(k, u):
    k = bytearray(k)
    k[0] &= 248
    k[31] &= 127
    k[31] |= 64
    k = int.from_bytes(bytes(k), "little")
    x1 = int.from_bytes(u, "little") % (2 ** 255)
    x2, z2, x3, z3, sw = 1, 0, x1, 1, 0
    for t in range(254, -1, -1):
        kt = (k >> t) & 1
        sw ^= kt
        x2, x3 = cswap(sw, x2, x3)
        z2, z3 = cswap(sw, z2, z3)
        sw = kt
        a = (x2 + z2) % P
        aa = a * a % P
        b = (x2 - z2) % P
        bb = b * b % P
        e = (aa - bb) % P
        c = (x3 + z3) % P
        d = (x3 - z3) % P
        da = d * a % P
        cb = c * b % P
        x3 = (da + cb) ** 2 % P
        z3 = x1 * (da - cb) ** 2 % P
        x2 = aa * bb % P
        z2 = e * (aa + A24 * e) % P
    x2, x3 = cswap(sw, x2, x3)
    z2, z3 = cswap(sw, z2, z3)
    return ((x2 * pow(z2, P - 2, P)) % P).to_bytes(32, "little")

t1 = time.monotonic_ns()
priv = bytearray(os.urandom(32))
priv[0] &= 248
priv[31] &= 127
priv[31] |= 64
priv = bytes(priv)
pub = x25519(priv, (9).to_bytes(32, "little"))
shared = x25519(priv, WPU)
proof = hashlib.sha256(label.encode() + shared).hexdigest()
span = time.monotonic_ns() - t1

sys.stdout.write("OPSPAN_NS:%d\n" % span)
sys.stdout.write("CLAIM:" + json.dumps({"proof_hex": proof, "label": label, "client_pub_hex": pub.hex()}) + "\n")
sys.stdout.flush()