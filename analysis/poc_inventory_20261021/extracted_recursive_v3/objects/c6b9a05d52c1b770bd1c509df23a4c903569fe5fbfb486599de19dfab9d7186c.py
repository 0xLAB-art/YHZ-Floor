import sys, json, time, secrets
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

SIG1 = "ac98a7678c1eff79b9dbe135bbbf71ba995c776b982c7fba6638d74f9f3105a4ea8089d7b2950d4e41fe94c24d81a658d94ff20e6f6e19e1f1e7268cd48d70a1"
SIG2 = "ac98a7678c1eff79b9dbe135bbbf71ba995c776b982c7fba6638d74f9f3105a46d7d3e745a3cc69a21721b469a6aa6047ac92b93424ebed1117e3379921732ae"
Z1   = "9b8c3525873fe8c4d2ee56d3df7f4a1f8ff61b14c3aacd53cbd6db9c3ab157ed"
Z2   = "080e1b6f687388402e73f6574237914dbbce931f696ba93e865b04c935b1eea5"
CH   = "78c8b3188007208146815e728960a111b13459f19585965b1ba7332d4dcc9eb2"

p  = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a  = p - 3
n  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
G  = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
     0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)

def padd(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P == Q:
        l = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        l = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (l * l - x1 - x2) % p
    return (x3, (l * (x1 - x3) - y1) % p)

def pmul(k, P):
    R = None
    while k:
        if k & 1: R = padd(R, P)
        P = padd(P, P); k >>= 1
    return R

def verify(d, z, r, s):
    if not (1 <= r < n and 1 <= s < n): return False
    w = pow(s, -1, n)
    P = padd(pmul(z * w % n, G), pmul(r * w % n, pmul(d, G)))
    return P is not None and P[0] % n == r

sig1 = bytes.fromhex(SIG1); sig2 = bytes.fromhex(SIG2)
z1 = int(Z1, 16); z2 = int(Z2, 16)
r1 = int(SIG1[:64], 16); s1 = int(SIG1[64:], 16)
r2 = int(SIG2[:64], 16); s2 = int(SIG2[64:], 16)

t0 = time.monotonic_ns()

# Repeated nonce: k = (z1-z2)/(e1*s1 - e2*s2), d = (e1*s1*k - z1)/r1
found = None
for e1 in (1, -1):
    for e2 in (1, -1):
        a1 = e1 * s1 % n
        a2 = e2 * s2 % n
        den = (a1 - a2) % n
        if den == 0: continue
        k = (z1 - z2) * pow(den, -1, n) % n
        if k == 0: continue
        d = (a1 * k - z1) * pow(r1, -1, n) % n
        if d == 0: continue
        if (verify(d, z1, r1, s1) or verify(d, z1, r1, n - s1)) and \
           (verify(d, z2, r2, s2) or verify(d, z2, r2, n - s2)):
            found = (d, k, e1, e2)
            break
    if found: break

if not found:
    sys.stderr.write("no solution\n")
    raise SystemExit(1)

d, k, e1, e2 = found

key = ECC.construct(curve='NIST P-256', d=d)
assert DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(Z1)), sig1)
assert DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(Z2)), sig2)

newsig = DSS.new(key, 'fips-186-3').sign(SHA256.new(bytes.fromhex(CH)))
assert DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(CH)), newsig)

t1 = time.monotonic_ns()
print("e1=%d e2=%d d=%064x k=%064x" % (e1, e2, d, k))
sys.stdout.flush()
print("CLAIM:" + json.dumps({"d_hex": format(d, '064x'), "sig_hex": newsig.hex()}, separators=(',', ':')))
print("OPSPAN_NS:" + str(t1 - t0))
sys.stdout.flush()