import json, sys, time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
P = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
A = P - 3
G = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
     0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)

sig1_hex = "da822297e4b4a337ea9cb6dfae78fed2769049f1f433f7066c31153333d869658e575b1822fa6b5891cf7f3fa9adcb86edecca92caabd2c466aa2296705177ce"
sig2_hex = "da822297e4b4a337ea9cb6dfae78fed2769049f1f433f7066c31153333d869656f31852edb0c6476db37d313d1ea3784b49eaeed2a6b43db07c620c42759ff74"
z1_hex = "6e496eed6c24f1b743b86f0fd7d188ead82025fbf550c3791f7f8e9d3a5a7053"
z2_hex = "04fb339b5809802c33c89b5bdbfc304f1c67d033bbaf87c95a538b1b3bf1d5af"
challenge_msg_hex = "f2e390af2dffdc4607db3f4859e04ad3e4402b27a6ae1b5d60116c22ab060364"

r1 = int(sig1_hex[0:64], 16)
s1 = int(sig1_hex[64:128], 16)
r2 = int(sig2_hex[0:64], 16)
s2 = int(sig2_hex[64:128], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)


def add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if p1 == p2:
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, P) % P
    else:
        lam = (y2 - y1) * pow((x2 - x1) % P, -1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def mul(k, p):
    if k < 0:
        k = (-k) % N
    res = None
    base = p
    while k:
        if k & 1:
            res = add(res, base)
        base = add(base, base)
        k >>= 1
    return res


def verify(dint, r_, s_, z):
    if not (1 <= dint < N and 1 <= r_ < N and 1 <= s_ < N):
        return False
    w = pow(s_, -1, N)
    u1 = z * w % N
    u2 = r_ * w % N
    Q = add(mul(u1, G), mul(u2, mul(dint, G)))
    if Q is None:
        return False
    return Q[0] % N == r_


t0 = time.monotonic_ns()

assert r1 == r2, 'r values differ'
r = r1

found = None
cands = []
for sig1 in (1, -1):
    for sig2 in (1, -1):
        den = (sig1 * s1 - sig2 * s2) % N
        if den == 0:
            continue
        num = (sig1 * z1 - sig2 * z2) % N
        k = num * pow(den, -1, N) % N
        if k == 0:
            continue
        d = ((sig1 * s1 * k - sig1 * z1) * pow(r, -1, N)) % N
        R = mul(k, G)
        rcons = R is not None and R[0] % N == r
        v1 = verify(d, r, s1, z1)
        v2 = verify(d, r, s2, z2)
        sys.stderr.write('combo %+d %+d k=%064x d=%064x R_ok=%s v1=%s v2=%s\n' % (sig1, sig2, k, d, rcons, v1, v2))
        cands.append((d, v1 and v2))
        if v1 and v2 and found is None:
            found = d

assert found is not None, 'no verifying candidate'
d = found

t1 = time.monotonic_ns()

key = ECC.construct(curve='NIST P-256', d=d)
sig3 = DSS.new(key, 'fips-186-3').sign(SHA256.new(bytes.fromhex(challenge_msg_hex)))
sig_hex = sig3.hex()
assert len(sig_hex) == 128
DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(challenge_msg_hex)), sig3)

sys.stderr.write('OPSPAN_NS:%d\n' % (t1 - t0))
print('CLAIM:' + json.dumps({'d_hex': '%064x' % d, 'sig_hex': sig_hex}), flush=True)