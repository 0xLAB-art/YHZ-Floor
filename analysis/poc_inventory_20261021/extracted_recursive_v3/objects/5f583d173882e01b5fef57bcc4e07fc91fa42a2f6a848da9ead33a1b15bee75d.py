import json, sys, time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
P = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
A = P - 3
B = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
GX = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
GY = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
Gx, Gy = GX, GY

sig1_hex = "da822297e4b4a337ea9cb6dfae78fed2769049f1f433f7066c31153333d869658e575b1822fa6b5891cf7f3fa9adcb86edecca92caabd2c466aa2296705177ce"
sig2_hex = "da822297e4b4a337ea9cb6dfae78fed2769049f1f433f7066c31153333d869656f31852edb0c6476db37d313d1ea3784b49eaeed2a6b43db07c620c42759ff74"
z1_hex = "6e496eed6c24f1b743b86f0fd7d188ead82025fbf550c3791f7f8e9d3a5a7053"
z2_hex = "04fb339b5809802c33c89b5bdbfc304f1c67d033bbaf87c95a538b1b3bf1d5af"
challenge_msg_hex = "f2e390af2dffdc4607db3f4859e04ad3e4402b27a6ae1b5d60116c22ab060364"

r = int(sig1_hex[0:64], 16)
s1 = int(sig1_hex[64:128], 16)
r2 = int(sig2_hex[64 - 0:64], 16)
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
        lam = (y2 - y1) * pow(x2 - x1, -1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def mul(k, p):
    res = None
    while k:
        if k & 1:
            res = add(res, p)
        p = add(p, p)
        k >>= 1
    return res


G = (Gx, Gy)


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


k = ((z1 - z2) * pow(s2 - s1, -1, N)) % N
d = ((s1 * k - z1) * pow(r, -1, N)) % N

ok1 = verify(d, r, s1, z1)
ok2 = verify(d, r, s2, z2)

R = mul(k, G)
Rok = R is not None and R[0] % N == r

sys.stderr.write("k=%064x\nd=%064x\nok1=%s ok2=%s R_consistent=%s\n" % (k, d, ok1, ok2, Rok))

z3 = int(challenge_msg_hex, 16)
k3 = int.from_bytes(bytes.fromhex(z3_hex_seed) if False else SHA256.new((challenge_msg_hex + "nonce").encode()).digest(), 'big')
k3 = (k3 % (N - 1)) + 1
R3 = mul(k3, G)
r3 = R3[0] % N
s3 = pow(k3, -1, N) * (z3 + r3 * d) % N
if s3 > N // 2:
    s3 = N - s3
raw = ("%064x%064x" % (r3, s3))

assert verify(d, r3, s3, z3), "self sig fail"
assert verify(d, r, s1, z1), "sig1 fail"
assert verify(d, r, s2, z2), "sig2 fail"

sys.stderr.write("raw len=%d verify3=ok\n" % len(raw))
print("CLAIM:" + json.dumps({"d_hex": "%064x" % d, "sig_hex": raw}), flush=True)