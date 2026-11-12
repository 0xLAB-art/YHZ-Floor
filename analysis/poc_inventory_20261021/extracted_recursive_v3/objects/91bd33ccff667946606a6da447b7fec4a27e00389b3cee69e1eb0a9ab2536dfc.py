import sys, json, time, secrets

SIG1 = "ac98a7678c1eff79b9dbe135bbbf71ba995c776b982c7fba6638d74f9f3105a4ea8089d7b2950d4e41fe94c24d81a658d94ff20e6f6e19e1f1e7268cd48d70a1"
SIG2 = "ac98a7678c1eff79b9dbe135bbbf71ba995c776b982c7fba6638d74f9f3105a46d7d3e745a3cc69a21721b469a6aa6047ac92b93424ebed1117e3379921732ae"
Z1 = "9b8c3525873fe8c4d2ee56d3df7f4a1f8ff61b14c3aacd53cbd6db9c3ab157ed"
Z2 = "080e1b6f687388402e73f6574237914dbbce931f696ba93e865b04c935b1eea5"
CH = "78c8b3188007208146815e728960a111b13459f19585965b1ba7332d4dcc9eb2"

p  = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a  = p - 3
b  = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
Gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
Gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
n  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

def inv(x, m):
    return pow(x % m, -1, m)

def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        l = (3 * x1 * x1 + a) * inv(2 * y1, p) % p
    else:
        l = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (l * l - x1 - x2) % p
    y3 = (l * (x1 - x3) - y1) % p
    return (x3, y3)

def mul(k, P):
    R = None
    while k:
        if k & 1:
            R = add(R, P)
        P = add(P, P)
        k >>= 1
    return R

G = (Gx, Gy)

def verify(d, z, sig):
    r = int.from_bytes(sig[:32], 'big')
    s = int.from_bytes(sig[32:64], 'big')
    if not (1 <= r < n and 1 <= s < n):
        return False
    w = inv(s, n)
    u1 = z * w % n
    u2 = r * w % n
    Pt = add(mul(u1, G), mul(u2, mul(d, G)))
    if Pt is None:
        return False
    return Pt[0] % n == r

sig1 = bytes.fromhex(SIG1)
sig2 = bytes.fromhex(SIG2)
z1 = int.from_bytes(bytes.fromhex(Z1), 'big')
z2 = int.from_bytes(bytes.fromhex(Z2), 'big')
r1 = int.from_bytes(sig1[:32], 'big')
s1 = int.from_bytes(sig1[32:64], 'big')
r2 = int.from_bytes(sig2[:32], 'big')
s2 = int.from_bytes(sig2[32:64], 'big')

t0 = time.monotonic_ns()

cands = []
for e1 in (1, -1):
    for e2 in (1, -1):
        a1 = e1 * s1 % n
        a2 = e2 * s2 % n
        den = (a1 - a2) % n
        if den == 0:
            continue
        k = (z1 - z2) * inv(den, n) % n
        denr = (a2 * r1 - a1 * r2) % n
        if denr == 0:
            continue
        d = (a2 * z1 - a1 * z2) * inv(denr, n) % n
        if d == 0:
            continue
        cands.append((e1, e2, k, d))

chosen = None
for e1, e2, k, d in cands:
    if verify(d, z1, sig1) and verify(d, z2, sig2):
        chosen = (d, k, e1, e2)
        break

if chosen is None:
    print("CLAIM:" + json.dumps({"d_hex": "00" * 32, "sig_hex": "00" * 64}, separators=(',', ':')))
    sys.stdout.flush()
    raise SystemExit(1)

d, k, e1, e2 = chosen

# sign the challenge message with the recovered key
zc = int.from_bytes(bytes.fromhex(CH), 'big')
while True:
    kk = secrets.randbelow(n - 1) + 1
    Pt = mul(kk, G)
    if Pt is None:
        continue
    rr = Pt[0] % n
    if rr == 0:
        continue
    ss = inv(kk, n) * (zc + rr * d) % n
    if ss == 0:
        continue
    if ss > n // 2:
        ss = n - ss
    break
newsig = rr.to_bytes(32, 'big') + ss.to_bytes(32, 'big')
assert verify(d, zc, newsig)

from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
key = ECC.construct(curve='NIST P-256', d=d)
assert DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(CH)), newsig)

t1 = time.monotonic_ns()
print("d", format(d, '064x'), "k", format(k, '064x'), "e", e1, e2, "sigverify", verify(d, zc, newsig))
sys.stdout.flush()
print("CLAIM:" + json.dumps({"d_hex": format(d, '064x'), "sig_hex": newsig.hex()}, separators=(',', ':')))
print("OPSPAN_NS:" + str(t1 - t0))
sys.stdout.flush()