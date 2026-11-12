import json, time
from hashlib import sha256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

prov = {
  "sig1_hex": "b39e1c124c1d6e5c6dbe275fd1ea329bc0b098908474179ef59ff10fb06c1a0fbe9eb0e1ca97422e0472d06de1cfa58914128657ab06bf35bc32b5e7621ea8a3",
  "sig2_hex": "b39e1c124c1d6e5c6dbe275fd1ea329bc0b098908474179ef59ff10fb06c1a0ff20bd8143c9bca33fce604d489acab5419c2319800c3a7d89c60e181633ff2bb",
  "z1_hex": "82455b97a235043fc5588250a59d1122b7bb10425d8f92248a9f4b02ec916d96",
  "z2_hex": "28b1dc7fcaeecc523468708c0e7a16b0e57cc200737514629e6865ca3a76916f",
  "challenge_msg_hex": "44f423961f599b0a88c064b2d0a71f8d1fea1d60ac7d8efe84b0b88aacf7e66c"
}

t0 = time.monotonic_ns()

N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

r1 = int(prov["sig1_hex"][:64], 16); s1 = int(prov["sig1_hex"][64:], 16)
r2 = int(prov["sig2_hex"][:64], 16); s2 = int(prov["sig2_hex"][64:], 16)
z1 = int(prov["z1_hex"], 16)
z2 = int(prov["z2_hex"], 16)

assert r1 == r2, "r mismatch"
r = r1

key_msg = bytes.fromhex(prov["challenge_msg_hex"])

def try_d(d):
    if not (1 <= d < N):
        return None
    try:
        pub = ECC.construct(curve="NIST P-256", d=d)
        key = ECC.EccKey(curve=pub.curve, point=pub.point)
        # verify original signature 1 under candidate d
        verifier = DSS.new(key, "fips-186-3", encoding="binary")
        try:
            verifier.verify(SHA256.new(bytes.fromhex(prov["z1_hex"])[:0] + b""), b"")
        except Exception:
            pass
        # direct ECDSA verify of sig1: s^-1 (z*G + r*Q) has x-coordinate == r
        from Crypto.Math.Numbers import Integer
        k1 = d * ECC.EccKey(curve="NIST P-256", point=ECC._curves["NIST P-256"].G) if False else None
        return pub
    except Exception:
        return None

def ecdsa_verify(d, msg_bytes, sig_hex):
    pub = ECC.construct(curve="NIST P-256", d=d)
    key = pub
    verifier = DSS.new(key, "fips-186-3", encoding="binary")
    try:
        verifier.verify(SHA256.new(msg_bytes), bytes.fromhex(sig_hex))
        return True
    except Exception:
        return False

# manual verify of sig1 under candidate d using point math (independent of DSS)
from Crypto.Math.Numbers import Integer
from Crypto.PublicKey.ECC import EccPoint

curve = ECC._curves["NIST P-256"]
G = curve.G
p = curve.p

def inv_mod(a, m=N):
    return pow(a, -1, m)

def verify_raw(d, z, r, s):
    if not (1 <= r < N and 1 <= s < N):
        return False
    Q = d * G
    w = inv_mod(s)
    u1 = (z * w) % N
    u2 = (r * w) % N
    R = u1 * G + u2 * Q
    x = int(R.x) % N
    return x == r

candidates = []
for s1v in (s1, (N - s1) % N):
    for s2v in (s2, (N - s2) % N):
        ds = (s1v - s2v) % N
        if ds == 0:
            continue
        dz = (z1 - z2) % N
        k = (dz * inv_mod(ds)) % N
        if k == 0:
            continue
        d = ((s1v * k - z1) * inv_mod(r)) % N
        if d == 0:
            continue
        if verify_raw(d, z1, r, s1v) and verify_raw(d, z2, r, s2v):
            candidates.append(d)

assert candidates, "no candidate"
d = candidates[0]

# sign challenge
priv = ECC.construct(curve="NIST P-256", d=d)
signer = DSS.new(priv, "fips-186-3", encoding="binary")
sig = signer.sign(SHA256.new(key_msg))
sig_hex = sig.hex()

# sanity: verify our signature
pub = ECC.construct(curve="NIST P-256", d=d)
ver = DSS.new(pub, "fips-186-3", encoding="binary")
try:
    ver.verify(SHA256.new(key_msg), sig)
except Exception as e:
    # fallback: adjust s to low-s if needed
    rr = int.from_bytes(sig[:32], "big")
    ss = int.from_bytes(sig[32:], "big")
    if ss > N // 2:
        ss = N - ss
    sig = rr.to_bytes(32, "big") + ss.to_bytes(32, "big")
    sig_hex = sig.hex()

d_hex = format(d, "064x")

t1 = time.monotonic_ns()
print(f"OPSPAN_NS:{t1 - t0}")
print("CLAIM:" + json.dumps({"d_hex": d_hex, "sig_hex": sig_hex}))
import sys
sys.stdout.flush()