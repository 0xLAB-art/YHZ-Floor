import json, time
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

P = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
A = P - 3
B = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
Gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
Gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5

def inv(x, m=N):
    return pow(x % m, -1, m)

def add(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    x1, y1 = p1; x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0: return None
    if p1 == p2:
        lam = (3 * x1 * x1 + A) * inv(2 * y1, P) % P
    else:
        lam = (y2 - y1) * inv(x2 - x1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)

def mul(k, pt):
    k %= N
    r = None
    while k:
        if k & 1: r = add(r, pt)
        pt = add(pt, pt)
        k >>= 1
    return r

G = (Gx, Gy)

def verify(z, r, s, Q):
    if not (1 <= r < N and 1 <= s < N): return False
    w = inv(s)
    u1 = z * w % N
    u2 = r * w % N
    pt = add(mul(u1, G), mul(u2, Q))
    if pt is None: return False
    return pt[0] % N == r

prov = json.loads(r'''{"sig1_hex": "46d811d6a069b7ac58593b928839f4402c3702bc346a592918ff676b39484c08219b3fc81afbccc72ed25ab763bdb9a4520d93505e9179805652e2c16bad1b57", "sig2_hex": "46d811d6a069b7ac58593b928839f4402c3702bc346a592918ff676b39484c08badfdb66a9a286e16d8c190b67a14e65de214e872f6c43083a0932db5ae0f268", "z1_hex": "169ef3d438000bac3db60f2ea2813f077c1a91812967096a825f90e0a1cfd7c2", "z2_hex": "209f791c6a0464d82a088b96280e53071b3674a584f70b895b078cfa08b18748", "challenge_msg_hex": "b81214e609927087594870f7cc65ca5ffb2c6631ba58c511153648ed49b60643", "curve": "NIST P-256"}''')

s1b = bytes.fromhex(prov['sig1_hex'])
s2b = bytes.fromhex(prov['sig2_hex'])
r1 = int.from_bytes(s1b[:32], 'big')
s1 = int.from_bytes(s1b[32:], 'big')
r2 = int.from_bytes(s2b[:32], 'big')
s2 = int.from_bytes(s2b[32:], 'big')
z1 = int(prov['z1_hex'], 16) % N
z2 = int(prov['z2_hex'], 16) % N
assert r1 == r2
r = r1

# derive nonce k directly first
k = ((z1 - z2) * inv(s1 - s2)) % N
d0 = ((s1 * k - z1) * inv(r)) % N

found = None
candidates = [(1, 1, k, d0)]
for e1 in (1, -1):
    for e2 in (1, -1):
        if (e1, e2) == (1, 1):
            continue
        ss1 = (e1 * s1) % N
        ss2 = (e2 * s2) % N
        den = (ss1 - ss2) % N
        if den == 0:
            continue
        kk = ((z1 - z2) * inv(den)) % N
        dd = ((ss1 * kk - z1) * inv(r)) % N
        candidates.append((e1, e2, kk, dd))

for e1, e2, kk, dd in candidates:
    Q = mul(dd, G)
    if Q is None:
        continue
    if verify(z1, r, s1, Q) and verify(z2, r, s2, Q):
        found = dd
        break

if found is None:
    print('CLAIM:' + json.dumps({'error': 'no candidate'}))
else:
    d = found
    key = ECC.construct(curve='NIST P-256', d=d)
    chg = bytes.fromhex(prov['challenge_msg_hex'])
    t0 = time.monotonic_ns()
    signer = DSS.new(key, 'fips-186-3')
    sig = signer.sign(SHA256.new(chg))
    t1 = time.monotonic_ns()
    print('OPSPAN_NS:' + str(t1 - t0))
    claim = {'d_hex': format(d, '064x'), 'sig_hex': sig.hex()}
    print('CLAIM:' + json.dumps(claim))