import time, sys, random, hashlib
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from Crypto.Util.asn1 import DerSequence

sig1_hex = "c7fdbb1e737577244f19d608a04e12f3e9b1e38f732d7c56d494c64eec4750096f091c4e52853ebc216e8244126b6b0e41ac035eff88a47146cae198cc035708"
sig2_hex = "c7fdbb1e737577244f19d608a04e12f3e9b1e38f732d7c56d494c64eec47500999728293b962da017303c1faefa4a5ec4e0b938553afc26254befb0c479de10a"
z1_hex = "e339518ec077d68b61ff868b51869dc8e7337a5dc27c4606075992fa8ddae7dc"
z2_hex = "7bf82a72193ed94794e534b195d94d3d39441ce73b892d62d5e942460c5cb8c6"
challenge_msg_hex = "08e22bef26c5879283807cba27ce16e0775bfb42cf481eae902120bb2f47c822"

p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
a = (-3) % p
G = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
     0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)

def padd(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    if P[0] == Q[0]:
        if (P[1] + Q[1]) % p == 0:
            return None
        lam = (3 * P[0] * P[0] + a) * pow(2 * P[1], -1, p) % p
    else:
        lam = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
    x = (lam * lam - P[0] - Q[0]) % p
    y = (lam * (P[0] - x) - P[1]) % p
    return (x, y)

def pmul(k, P):
    R = None
    k %= n
    while k:
        if k & 1:
            R = padd(R, P)
        P = padd(P, P)
        k >>= 1
    return R

def verify_ecdsa(d, r, s, z):
    if not (1 <= r < n and 1 <= s < n) or not (1 <= d < n):
        return False
    w = pow(s, -1, n)
    R = padd(pmul(z * w % n, G), pmul(r * w % n, pmul(d, G)))
    return R is not None and (R[0] % n) == r

def der(r, s):
    return DerSequence([r, s]).encode()

t0 = time.monotonic_ns()

sig1 = bytes.fromhex(sig1_hex)
sig2 = bytes.fromhex(sig2_hex)
r1 = int(sig1[:32].hex(), 16)
s1 = int(sig1[32:].hex(), 16)
r2 = int(sig2[:32].hex(), 16)
s2 = int(sig2[32:].hex(), 16)
z1 = int(z1_hex, 16) % n
z2 = int(z2_hex, 16) % n

d = None
if r1 == r2 and r1 != 0:
    for e1 in (1, -1):
        for e2 in (1, -1):
            ds = (e1 * s1 - e2 * s2) % n
            if ds == 0:
                continue
            k = ((z1 - z2) % n) * pow(ds, -1, n) % n
            if k == 0:
                continue
            cand = ((e1 * s1 * k - z1) * pow(r1, -1, n)) % n
            if cand == 0:
                continue
            if not (verify_ecdsa(cand, r1, s1, z1) and verify_ecdsa(cand, r2, s2, z2)):
                continue
            try:
                key = ECC.construct(curve='NIST P-256', d=cand)
                DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(z1_hex)), der(r1, s1))
                DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(z2_hex)), der(r2, s2))
            except Exception:
                continue
            d = cand
            break
        if d is not None:
            break

if d is None:
    raise SystemExit("recovery failed")

key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
msg = bytes.fromhex(challenge_msg_hex)
h = SHA256.new(msg)
zc = int(h.hexdigest(), 16) % n

r3 = s3 = None
for _ in range(200):
    k = random.SystemRandom().randrange(1, n)
    R = pmul(k, G)
    rr = R[0] % n
    if rr == 0:
        continue
    ss = pow(k, -1, n) * (zc + rr * d) % n
    if ss == 0:
        continue
    if ss > n // 2:
        ss = n - ss
    if not verify_ecdsa(d, rr, ss, zc):
        continue
    try:
        signer.verify(h, der(rr, ss))
    except Exception:
        continue
    r3, s3 = rr, ss
    break

if r3 is None:
    raw = signer.sign(h)
    r3 = int(raw[4:4 + 32].hex(), 16) if raw[0] == 0x30 else None
    if r3 is None:
        raise SystemExit("sign failed")
    s3 = int(raw[len(raw) - 32:].hex(), 16)

t1 = time.monotonic_ns()
print('OPSPAN_NS:%d' % (t1 - t0))
print('CLAIM:' + '{"d_hex": "%064x", "sig_hex": "%064x%064x"}' % (d, r3, s3))
sys.stdout.flush()