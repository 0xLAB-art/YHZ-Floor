import time, random, sys

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

def verify(d, r, s, z):
    if not (1 <= r < n and 1 <= s < n) or not (1 <= d < n):
        return False
    w = pow(s, -1, n)
    u1 = z * w % n
    u2 = r * w % n
    R = padd(pmul(u1, G), pmul(u2, pmul(d, G)))
    return R is not None and (R[0] % n) == r

t0 = time.monotonic_ns()

sig1 = bytes.fromhex(sig1_hex)
sig2 = bytes.fromhex(sig2_hex)
r1 = int(sig1[:32].hex(), 16)
s1 = int(sig1[32:].hex(), 16)
r2 = int(sig2[:32].hex(), 16)
s2 = int(sig2[32:].hex(), 16)
z1 = int(z1_hex, 16) % n
z2 = int(z2_hex, 16) % n
zc = int(challenge_msg_hex, 16) % n

if r1 != r2:
    raise SystemExit("r mismatch")

found = None
for e1 in (1, -1):
    for e2 in (1, -1):
        a1 = e1 * s1
        a2 = e2 * s2
        ds = (a1 - a2) % n
        dz = (z1 - z2) % n
        if ds == 0:
            continue
        k = dz * pow(ds, -1, n) % n
        if k == 0:
            continue
        d = ((a1 * k - z1) * pow(r1, -1, n)) % n
        if d == 0:
            continue
        if verify(d, r1, s1, z1) and verify(d, r2, s2, z2):
            found = d
            break
    if found:
        break

if found is None:
    raise SystemExit("recovery failed")

d = found
while True:
    k = random.SystemRandom().randrange(1, n)
    R = pmul(k, G)
    r3 = R[0] % n
    if r3 == 0:
        continue
    s3 = pow(k, -1, n) * (zc + r3 * d) % n
    if s3 == 0:
        continue
    if s3 > n // 2:
        s3 = n - s3
    break

assert verify(d, r3, s3, zc)

d_hex = '%064x' % d
sig_hex = '%064x%064x' % (r3, s3)
t1 = time.monotonic_ns()
print('OPSPAN_NS:%d' % (t1 - t0))
print('CLAIM:' + '{"d_hex": "%s", "sig_hex": "%s"}' % (d_hex, sig_hex))
sys.stdout.flush()