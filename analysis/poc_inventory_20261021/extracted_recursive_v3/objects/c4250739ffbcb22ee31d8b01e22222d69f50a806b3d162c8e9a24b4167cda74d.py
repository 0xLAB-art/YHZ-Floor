import sys, json, hashlib, re

from Crypto.PublicKey import ECC
from Crypto.Protocol import DH

CLAIM_PATHS = [
    "/", "/tls", "/tls/negotiate", "/negotiate", "/handshake", "/session",
    "/weak", "/downgrade", "/label", "/params", "/parameters", "/info",
    "/status", "/health", "/hello", "/api/tls", "/api/negotiate",
    "/v1/tls", "/cipher", "/suite", "/suites", "/config", "/policy",
    "/challenge", "/proof", "/verify", "/legacy", "/negotiated",
]

LABEL_KEYS = ("label", "cipher", "cipher_suite", "suite", "negotiated",
 "negotiated_label", "label_hex", "weak_label", "param",
              "parameters", "name", "value", "downgraded_label")


def ask(method, path, body=None):
    msg = {"http": {"method": method, "path": path}}
    if body is not None:
        msg["http"]["body"] = body
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return None


def b64d(s):
    import base64
    try:
        return base64.b64decode(s + "=" * (-len(s) % 4))
    except Exception:
        return b""


def harvest(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            if isinstance(v, str):
                if kl in LABEL_KEYS and ("TLS_" in v or "WITH" in v or "_" in v):
                    out.append(v)
                if kl in LABEL_KEYS and v:
                    out.append(v)
            else:
                harvest(v, out)
    elif isinstance(obj, list):
        for v in obj:
            harvest(v, out)


def find_label(reply):
    if not reply:
        return None
    raw = b64d(reply.get("body_b64", ""))
    txt = raw.decode("utf-8", "replace")
    cands = []
    try:
        harvest(json.loads(txt), cands)
    except Exception:
        pass
    for m in re.findall(r"TLS[_-][A-Za-z0-9_\-]+", txt):
        cands.append(m)
    for m in re.findall(r"[A-Z0-9_]*WITH_[A-Z0-9_]+", txt):
        cands.append(m)
    for c in cands:
        if not c:
            continue
        c2 = c
        if c2.lower().startswith("0x"):
            try:
                c2 = bytes.fromhex(c2[2:]).decode("ascii")
            except Exception:
                c2 = c
        return c2
    return None


def probe(paths, method="GET", body=None, hdrs=None):
    for p in paths:
        m = {"http": {"method": method, "path": p}}
        if hdrs:
            m["http"]["headers"] = hdrs
        if body is not None:
            m["http"]["body"] = body
        sys.stdout.write(json.dumps(m) + "\n")
        sys.stdout.flush()
        line = sys.stdin.readline()
        if not line:
            return None
        try:
            reply = json.loads(line)
        except Exception:
            continue
        sys.stderr.write("PROBE %s %s -> %s\n" % (method, p, line[:400]))
        lab = find_label(reply)
        if lab:
            sys.stderr.write("LABEL %r from %s\s\n" % (lab, p))
            return lab
    return None


def main():
    import time
    t0 = time.monotonic_ns()
    label = probe(CLAIM_PATHS)
    if label is None:
        alt = ["/tls?force=legacy", "/tls?downgrade=1", "/negotiate?suite=weak",
               "/handshake?legacy=1", "/tls/legacy", "/tls/weak",
               "/api/tls?downgrade=true", "/v1/negotiate"]
        label = probe(alt)
    if label is None:
        hdr = {"X-TLS-Downgrade": "legacy", "Accept": "text/plain"}
        label = probe(["/tls", "/", "/negotiate"], hdrs=hdr)

    weak_pub = bytes.fromhex(
        "500d28db2a460e4994785c062008fcfd1d56001f200678a5f2d91404ad91567c")

    priv = ECC.generate(curve="curve25519")
    pub = priv.public_key().export_key(format="raw")
    if len(pub) != 32:
        pub = pub[-32:]
    peer = ECC.import_key(
        b"-----BEGIN PUBLIC KEY-----\n" +
        __import__("base64").encodebytes(
            __import__("Crypto.Util.asn1", fromlist=["DerSequence"]).DerSequence().encode(x) 
            if False else b"").decode() or b"", b"" ) if False else None

    from Crypto.PublicKey import ECC as _ECC
    try:
        from Crypto.PublicKey import ECC
        peer = ECC.EccKey(curve="curve25519", point_x=int.from_bytes(weak_pub, "big"),
                          point_y=2)
    except Exception:
        peer = None

    shared = None
    if peer is not None:
        try:
            shared = DH.key_agreement(priv.public_key(), peer)
        except Exception as e:
            sys.stderr.write("dh1 fail %s\n" % e)

    if shared is None or len(shared) != 32:
        # manual X25519 (RFC 7748) fallback
        try:
            k = priv.export_key(format="raw")
        except Exception:
            k = None
        if k is None:
            d = priv.d
            k = b"\x00" *32 if d.bit_length() > 255 else (32 - ((d.bit_length() + 7) // 8)).to_bytes(1, "big") * 0 or (d | (1 << 254)).to_bytes(32, "big")
        k = bytearray(k)
        k[0] &= 248
        k[31] &= 127
        k[31] |= 64
        k = int.from_bytes(bytes(k), "little")
        P = 2 ** 255 - 19
        u = int.from_bytes(weak_pub, "little") & ((1 << 255) - 1)
        x1, x2, z2, x3, z3, swap = u, 1, 0, u, 1, 0
        for t in range(254, -1, -1):
            kt = (k >> t) & 1
            if swap ^ kt:
                x2, x3 = x3, x2
                z2, z3 = z3, z2
            swap = kt
            A = (x2 + z2) % P
            AA = A * A % P
            B = (x2 - z2) % P
            BB = B * B % P
            E = (AA - BB) % P
            C = (x3 + z3) % P
            D = (x3 - z3) % P
            DA = D * A % P
            CB = C * B % P
            x3 = (DA + CB) % P
            x3 = x3 * x3 % P
            z3 = (DA - CB) % P
            z3 = x1 * z3 % P * z3 % P
            x2 = AA * BB % P
            z2 = E * ((AA + 121665 * E) % P) % P
        if swap:
            x2, x3 = x3, x2
            z2, z3 = z3, z2
        shared = (x2 * pow(z2, P - 2, P) % P).to_bytes(32, "little")

    sys.stderr.write("label=%r shared=%s\n" % (label, shared.hex() if shared else None))

    if label is None:
        sys.stdout.write("CLAIM:" + json.dumps({"proof_hex": "", "label": "unknown",
                                                  "client_pub_hex": pub.hex()}) + "\n")
        sys.stdout.flush()
        return

    lb = label.encode("utf-8")
    proof = hashlib.sha256(lb + shared).hexdigest()
    sys.stdout.write("OPSPAN_NS:%d\n" % (time.monotonic_ns() - t0))
    sys.stdout.write("CLAIM:" + json.dumps({"proof_hex": proof, "label": label,
                                              "client_pub_hex": pub.hex()}) + "\n")
    sys.stdout.flush()


main()