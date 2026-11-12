import sys, json, hashlib, re
from base64 import b64decode

WEAK = bytes.fromhex("a59474c779ffc7b42f9fd84bd8efef6316540987510f7b8cfe72cd2c56d7a233")

def req(method, path, body=None, headers=None):
    msg = {"http": {"method": method, "path": path}}
    if body is not None:
        msg["http"]["body"] = body
    if headers:
        msg["http"]["headers"] = headers
    try:
        sys.stdout.write(json.dumps(msg) + "\n"); sys.stdout.flush()
    except Exception:
        return None
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return None

def body_of(r):
    try:
        return b64decode(r.get("body_b64", ""))
    except Exception:
        return b""

def harvest(txt):
    out = []
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                kl = str(k).lower()
                if isinstance(v, str) and ("label" in kl or "cipher" in kl or "suite" in kl or "negoti" in kl or kl == "tls" or "proto" in kl):
                    out.append(v)
                elif isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    try:
        walk(json.loads(txt))
    except Exception:
        pass
    for m in re.findall(r"\bTLS[_A-Z0-9]*_[A-Z0-9_]+\b", txt):
        out.append(m)
    for m in re.findall(r"\b(?:TLSv1(?:\.\d)?|SSL3(?:\.0)?)\b", txt):
        out.append(m)
    return out

PATHS = ["/", "/index", "/info", "/status", "/tls", "/tls/negotiate", "/negotiate",
         "/handshake", "/tls/handshake", "/downgrade", "/tls/downgrade",
         "/session", "/tls/session", "/weak", "/suite", "/cipher", "/v1/negotiate",
         "/api/negotiate", "/health"]

labels = []
bodies = []
for p in PATHS:
    r = req("GET", p)
    if not r:
        continue
    b = body_of(r)
    txt = b.decode("utf-8", "replace")
    bodies.append((p, r.get("status"), txt[:2000]))
    labels.extend(harvest(txt))

FALLBACK = ["TLS_RSA_WITH_AES_128_CBC_SHA", "TLS_RSA_WITH_AES_128_CBC_SHA256",
            "TLS_RSA_WITH_3DES_EDE_CBC_SHA", "DHE-RSA-AES128-SHA",
            "TLS_RSA_WITH_NULL_SHA", "TLS_RSA_WITH_AES_256_CBC_SHA",
            "TLSv1", "SSLv3"]

label = None
if labels:
    for l in labels:
        if "TLS_" in l or l.startswith("TLSv") or l.startswith("SSL"):
            label = l
            break
 if label is None:
        label = labels[0]
else:
    label = FALLBACK[0]

label = label.strip()

# X25519 (RFC 7748)
P = 2 ** 255 - 19
A24 = 121665

def cswap(swap, x2, x3):
    dummy = swap * ((x2 - x3) % P)
    return (x2 - dummy) % P, (x3 + dummy) % P

def x25519(k_bytes, u_bytes):
    k = bytearray(k_bytes)
    k[0] &= 248; k[31] &= 127; k[31] |= 64
    k = int.from_bytes(bytes(k), "little")
    x1 = int.from_bytes(u_bytes, "little") % (2 ** 255)
    x2, z2, x3, z3, swap = 1, 0, x1, 1, 0
    for t in range(254, -1, -1):
        kt = (k >> t) & 1
        swap ^= kt
        x2, x3 = cswap(swap, x2, x3)
        z2, z3 = cswap(swap, z2, z3)
        swap = kt
        a = (x2 + z2) % P; aa = a * a % P
        b = (x2 - z2) % P; bb = b * b % P
        e = (aa - bb) % P
        c = (x3 + z3) % P; d = (x3 - z3) % P
        da = d * a % P; cb = c * b % P
        x3 = (da + cb) % P; x3 = x3 * x3 % P
        z3 = (da - cb) % P; z3 = x1 * z3 % P * z3 % P
        x2 = aa * bb % P
        z2 = e * ((aa + A24 * e) % P) % P
    x2, x3 = cswap(swap, x2, x3)
    z2, z3 = cswap(swap, z2, z3)
    return ((x2 * pow(z2, P - 2, P)) % P).to_bytes(32, "little")

priv = hashlib.sha256(os.urandom(32) + b"acts-downgrade").digest() if False else None
import os
priv = os.urandom(32)
pub = x25519(priv, (9).to_bytes(32, "little"))
shared = x25519(priv, WEAK)
proof = hashlib.sha256(label.encode() + shared).hexdigest()

print("CLAIM:" + json.dumps({"proof_hex": proof, "label": label, "client_pub_hex": pub.hex()}, separators=(",", ":")))