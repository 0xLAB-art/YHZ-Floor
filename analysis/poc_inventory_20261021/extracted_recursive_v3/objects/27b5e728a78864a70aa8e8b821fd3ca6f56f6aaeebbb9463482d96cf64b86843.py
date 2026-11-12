import json
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

sig1_hex = "7c136b57aac33ad2ca67810aa1c052a39c4c2c39a0cfe8da2fc7ea28d419decb8a8e47cddeff574a9b508b61431c41532f87d6c6348f5654ebad469d0b5b6259"
sig2_hex = "7c136b57aac33ad2ca67810aa1c052a39c4c2c39a0cfe8da2fc7ea28d419decb37d75e003be88bf284a2c211a82746aa3fc1b9a33ef652727df479c44cfd7c5b"
z1_hex = "3c01ab82de5471e7f11612c49d4f538d82a432c843ca75f38f4433da4e773c10"
z2_hex = "0dee3e18e96da07d8d95c1cf607977cd3d8bfffaa083a9117580152fb00b42a1"
challenge_msg_hex = "8fa2e0a5be74ad292bcbf765b27ed3993f99255dde648b4763e14159f5a50cf4"

p  = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a  = p - 3
b  = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
Gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
Gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
n  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
G  = (Gx, Gy)

def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0] and (P[1] + Q[1]) % p == 0: return None
    if P == Q:
        lam = (3 * P[0] * P[0] + a) * pow(2 * P[1], -1, p) % p
    else:
        lam = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
    x = (lam * lam - P[0] - Q[0]) % p
    y = (lam * (P[0] - x) - P[1]) % p
    return (x, y)

def mul(k, P):
    k %= n
    R = None
    while k:
        if k & 1: R = add(R, P)
        P = add(P, P)
        k >>= 1
    return R

def verify(Q, z, r, s):
    if not (1 <= r < n and 1 <= s < n): return False
    w = pow(s, -1, n)
    X = add(mul(z * w % n, G), mul(r * w % n, Q))
    return X is not None and X[0] % n == r

r1 = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:], 16)
r2 = int(sig2_hex[:64], 16)
s2 = int(sig2_hex[64:], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)
r = r1

best = None
for f1 in (0, 1):
    for f2 in (0, 1):
        t1 = s1 if f1 == 0 else n - s1
        t2 = s2 if f2 == 0 else n - s2
        if (t1 - t2) % n == 0 or r == 0:
            continue
        try:
            k = (z1 - z2) * pow((t1 - t2) % n, -1, n) % n
            d = ((t1 * k - z1) * pow(r, -1, n)) % n
        except Exception:
            continue
        if not (1 <= d < n):
            continue
        Q = mul(d, G)
        if Q is None:
            continue
        if verify(Q, z1, r1, s1) and verify(Q, z2, r2, s2):
            best = (f1, f2, d)
            break
    if best: break

if best is None:
    k = (z1 - z2) * pow((s1 - s2) % n, -1, n) % n
    d = ((s1 * k - z1) * pow(r, -1, n)) % n
    best = (0, 0, d)

d = best[2]

key = ECC.construct(curve="NIST P-256", d=d)
signer = DSS.new(key, "fips-186-3")
msg = bytes.fromhex(challenge_msg_hex)
sig = signer.sign(SHA256.new(msg))
signer.verify(SHA256.new(msg), sig)

print("CLAIM:" + json.dumps({"d_hex": "%064x" % d, "sig_hex": sig.hex()}, separators=(",", ":")))