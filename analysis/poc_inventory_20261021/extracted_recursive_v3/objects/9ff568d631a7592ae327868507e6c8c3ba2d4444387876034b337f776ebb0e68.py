import sys, json, re, os
from base64 import b64decode

RESP = []

def call(method, path, body=None, headers=None):
    msg = {"http": {"method": method, "path": path}}
    if body is not None:
        msg["http"]["body"] = body
    if headers:
        msg["http"]["headers"] = headers
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        RESP.append({"path": path, "method": method, "status": 0, "text": "", "raw": b""})
        return
    line = line.strip()
    try:
        r = json.loads(line)
    except Exception:
        RESP.append({"path": path, "method": method, "status": -1, "text": line, "raw": b""})
        return
    raw = b""
    b64 = r.get("body_b64") or ""
    if b64:
        try:
            raw = b64decode(b64)
        except Exception:
            raw = b""
    text = raw.decode("utf-8", "replace")
    RESP.append({"path": path, "method": method, "status": r.get("status"),
                 "text": text, "raw": raw, "ct": r.get("content_type", "")})

prov = {}
try:
    if len(sys.argv) > 1:
        prov = json.loads(sys.argv[1])
except Exception:
    prov = {}

weak_pub_hex = prov.get("weak_pub_hex", "212499c1c89e339865ce893148abbd668e841c3c6d7172da775d32309529405c")

sys.stderr.write("INFO provision " + json.dumps(prov) + "\n")

LEGACY = [
    "TLS_RSA_EXPORT_WITH_RC4_40_MD5",
    "TLS_RSA_EXPORT_WITH_RC2_CBC_40_MD5",
    "TLS_RSA_EXPORT_WITH_DES40_CBC_SHA",
    "TLS_RSA_WITH_RC4_128_MD5",
    "TLS_RSA_WITH_RC4_128_SHA",
    "TLS_RSA_WITH_3DES_EDE_CBC_SHA",
    "TLS_RSA_WITH_DES_CBC_SHA",
]

# ---------- phase 1: surface discovery ----------
PATHS = [
    "/", "/index", "/index.html", "/health", "/healthz", "/status", "/info",
    "/tls", "/tls/", "/tls/negotiate", "/tls/handshake", "/tls/policy",
    "/tls/ciphers", "/tls/suites", "/tls/status", "/tls/downgrade",
    "/negotiate", "/handshake", "/policy", "/params", "/parameters",
    "/cipher", "/ciphers", "/cipher-suites", "/suites", "/supported",
    "/downgrade", "/legacy", "/session", "/weak", "/peer", "/server",
    "/api", "/api/tls", "/api/negotiate", "/api/handshake", "/api/policy",
    "/api/ciphers", "/api/cipher", "/api/params", "/v1", "/v1/negotiate",
    "/config", "/settings", "/meta", "/hello", "/version", "/probe",
    "/negotiation", "/tls_negotiate", "/clienthello", "/client-hello",
    "/offer", "/choose", "/connect", "/start", "/open", "/challenge",
]
for p in PATHS:
    call("GET", p)

# ---------- phase 2: drive the downgrade explicitly ----------
NE = ["/negotiate", "/tls/negotiate", "/handshake", "/tls/handshake",
      "/api/negotiate", "/api/handshake", "/tls", "/negotiation", "/offer",
      "/choose", "/session", "/connect", "/v1/negotiate"]

def urlencode(s):
    out = []
    for ch in s:
        if ch.isalnum() or ch in "-_.~":
            out.append(ch)
        else:
            out.extend("%%%02X" % b for b in ch.encode())
    return "".join(out)

QUERYS = ["?cipher={s}", "?cipher_suite={s}", "?suite={s}", "?tls_cipher_suite={s}",
          "?ciphersuite={s}", "?offer={s}", "?cypher={s}", "?tls={s}", "?cipher_suites={s}"]

for suite in LEGACY:
    for base in NE:
        for qt in QUERYS:
            call("GET", base + qt.format(s=urlencode(suite)))
        call("POST", base, body=json.dumps({"cipher_suite": suite}),
             headers={"Content-Type": "application/json"})
        call("POST", base, body=json.dumps({"cipher_suites": [suite]}),
             headers={"Content-Type": "application/json"})
        call("POST", base, body=json.dumps({"offer": suite}),
             headers={"Content-Type": "application/json"})
        call("GET", base, headers={"X-Cipher-Suite": suite, "X-Offered-Ciphers": suite,
                                    "X-TLS-Cipher-Suite": suite})

# ---------- phase 3: mine the negotiated label ----------
CANDS = []
SUITE_RE = re.compile(r"TLS[-_ ][A-Za-z0-9]+(?:[-_ ][A-Za-z0-9]+){1,7}")

def harvest(text):
    out = []
    try:
        obj = json.loads(text)
        flat = json.dumps(obj)
    except Exception:
        flat = text
    for m in SUITE_RE.finditer(flat):
        s = m.group(0).strip().rstrip(",.;\"'\n)").strip()
        s = re.sub(r"\s+", "_", s)
        s = re.sub(r"[-_ ]+", "_", s)
        s = s.upper()
        if 8 <= len(s) <= 90:
            out.append(s)
    return out

KEY_RE = re.compile(r"\"(label|cipher|cipher_suite|cipherSuite|suite|negotiated|selected|result|value|name)\"\s*:\s*\"([^\"]+)\"", re.I)
keyed = []
for e in RESP:
    for k, v in KEY_RE.findall(e["text"]):
        vv = re.sub(r"[-_ ]+", "_", v.strip()).upper()
        if vv.startswith("TLS"):
            keyed.append(vv)
    CANDS.extend(harvest(e["text"]))

sys.stderr.write("INFO responses=%d\n" % len(RESP))
for e in RESP:
    t = e["text"].replace("\n", " ")[:300]
    if t and e["status"] not in (404, 0, -1):
        sys.stderr.write("INFO %s %s -> %s | %s\n" % (e["method"], e["path"], e["status"], t))
sys.stderr.write("INFO keyed=%s\n" % json.dumps(keyed[:40]))
sys.stderr.write("INFO cands=%s\n" % json.dumps(CANDS[:60]))

WEAK = ("EXPORT", "RC4", "RC2", "DES", "NULL", "ANON", "MD5", "EXP", "3DES", "CBC", "ENCRYPT")

def score(s):
    sc = 0
    for k in WEAK:
        if k in s:
            sc += 1
    return sc

label = None
pool = []
for s in keyed:
    if s not in pool:
        pool.append(s)
for s in CANDS:
    if s not in pool:
        pool.append(s)
if pool:
    best = max(pool, key=lambda s: (score(s), pool.index(s) == 0, -pool.index(s)))
    label = best
if label is None:
    label = "TLS_RSA_EXPORT_WITH_RC4_40_MD5"

sys.stderr.write("INFO label=%s\n" % label)

# ---------- phase 4: compute the claim ----------
from Crypto.PublicKey import ECC
from Crypto.Protocol.DH import key_agreement
import hashlib

t0 = __import__("time").monotonic_ns()
priv = ECC.generate(curve="ed25519")
pub = priv.public_key()
peer = ECC.import_key("04" + weak_pub_hex)
try:
    shared = key_agreement(priv, peer, kdf=lambda k: k)
except Exception:
    priv = ECC.generate(curve="Curve25519")
    pub = priv.public_key()
    peer = ECC.import_key("04" + weak_pub_hex)
    shared = key_agreement(priv, peer, kdf=lambda k: k)
proof = hashlib.sha256(label.encode() + shared).hexdigest()
pub_hex = pub.pointQ.x.to_bytes(32, "big").hex()
t1 = __import__("time").monotonic_ns()

claim = {"proof_hex": proof, "label": label, "client_pub_hex": pub_hex}
sys.stderr.write("INFO claim=%s\n" % json.dumps(claim))
print("OPSPAN_NS:%d" % (t1 - t0), flush=True)
print("CLAIM:" + json.dumps(claim, separators=(",", ":")), flush=True)