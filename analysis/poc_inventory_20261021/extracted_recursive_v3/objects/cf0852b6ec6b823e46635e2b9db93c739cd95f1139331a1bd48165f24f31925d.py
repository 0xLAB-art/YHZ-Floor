import sys, json, time

t0 = time.monotonic_ns()

sig1_hex = "c1cf267afd0f898fcd7b52bb5baac12160ffa5e58b5cb179763c2d3d295798dc08f0b8bf3eff8b2678c3fc45d9d10c02e9595b046e5696c40c12449e468a73c9"
sig2_hex = "c1cf267afd0f898fcd7b52bb5baac12160ffa5e58b5cb179763c2d3d295798dc9bb94b9198774842b0ef032cc9d805b80e798490f51961d9e4cce9419f8160d4"
z1_hex = "bfe5dafc63a20de42441eec226138632d9cf33e82e18ea46ff1cd09dd56e8dd1"
z2_hex = "4ea1bbac33f8928a0ef148b617688adf07edf38741fddcec676cf7c0b393b898"
challenge_msg_hex = "b13d5aebc4684b1e250fc69fb0c37066c17808c166e849f6cabdd6e9adc034f4"

from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Signature import DSS

N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

sig1 = bytes.fromhex(sig1_hex)
sig2 = bytes.fromhex(sig2_hex)
r = int.from_bytes(sig1[:32], "big")
s1 = int.from_bytes(sig1[32:], "big")
s2 = int.from_bytes(sig2[32:], "big")
r2 = int.from_bytes(sig2[:32], "big")
z1 = int(z1_hex, 16) % N
z2 = int(z2_hex, 16) % N

assert r == r2

G = ECC.construct(curve="NIST P-256", d=1).pointQ

def verify_pair(d):
    if not (1 <= d < N):
        return False
    try:
        Q = ECC.construct(curve="NIST P-256", d=d).pointQ
    except Exception:
        return False
    for z, s in ((z1, s1), (z2, s2)):
        if s % N == 0:
            return False
        w = pow(s, -1, N)
        u1 = (z * w) % N
        u2 = (r * w) % N
        try:
            R = u1 * G + u2 * Q
        except Exception:
            return False
        if R.x % N != r:
            return False
    return True

d_found = None
for s1c in (s1, (-s1) % N):
    for s2c in (s2, (-s2) % N):
        ds = (s1c - s2c) % N
        if ds == 0:
            continue
        k = ((z1 - z2) * pow(ds, -1, N)) % N
        if k == 0:
            continue
        d = ((s1c * k - z1) * pow(r, -1, N)) % N
        if verify_pair(d):
            d_found = d
            break
    if d_found is not None:
        break

if d_found is None:
    print(json.dumps({"error": "recovery failed"}))
    sys.stdout.flush()
    print("CLAIM:" + json.dumps({"d_hex": "", "sig_hex": ""}))
    sys.stdout.flush()
    sys.exit(1)

d = d_found
key = ECC.construct(curve="NIST P-256", d=d)
msg = bytes.fromhex(challenge_msg_hex)
h = SHA256.new(msg)
sig = DSS.new(key, "fips-186-3").sign(h)
r_c = int.from_bytes(sig[:32], "big")
s_c = int.from_bytes(sig[32:], "big")
if s_c > N // 2:
    s_c = N - s_c
sig_hex = r_c.to_bytes(32, "big").hex() + s_c.to_bytes(32, "big").hex()

assert verify_pair(d)

t1 = time.monotonic_ns()
print("OPSPAN_NS:" + str(t1 - t0))
sys.stdout.flush()
print("CLAIM:" + json.dumps({"d_hex": "%064x" % d, "sig_hex": sig_hex}))
sys.stdout.flush()