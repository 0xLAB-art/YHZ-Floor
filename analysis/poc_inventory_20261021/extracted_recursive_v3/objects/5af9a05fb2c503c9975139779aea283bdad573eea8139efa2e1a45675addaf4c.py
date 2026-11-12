import json
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from Crypto.Util.number import inverse

sig1_hex = "7c136b57aac33ad2ca67810aa1c052a39c4c2c39a0cfe8da2fc7ea28d419decb8a8e47cddeff574a9b508b61431c41532f87d6c6348f5654ebad469d0b5b6259"
sig2_hex = "7c136b57aac33ad2ca67810aa1c052a39c4c2c39a0cfe8da2fc7ea28d419decb37d75e003be88bf284a2c211a82746aa3fc1b9a33ef652727df479c44cfd7c5b"
z1_hex = "3c01ab82de5471e7f11612c49d4f538d82a432c843ca75f38f4433da4e773c10"
z2_hex = "0dee3e18e96da07d8d95c1cf607977cd3d8bfffaa083a9117580152fb00b42a1"
challenge_msg_hex = "8fa2e0a5be74ad292bcbf765b27ed3993f99255dde648b4763e14159f5a50cf4"

curve = ECC._curves["NIST P-256"]
n = int(curve.order)
p = int(curve.p)
a = int(curve.a)
Gx = int(curve.Gx)
Gy = int(curve.Gy)

r1 = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:], 16)
r2 = int(sig2_hex[:64], 16)
s2 = int(sig2_hex[64:], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

assert r1 == r2
r = r1

k = (z1 - z2) * inverse((s1 - s2) % n, n) % n
d = ((s1 * k - z1) * inverse(r, n)) % n
assert 1 <= d < n

# algebraic self-check against the ECDSA equation s = k^-1 (z + r d)
assert (z1 + r * d) * inverse(s1, n) % n == k
assert (z2 + r * d) * inverse(s2, n) % n == k

# independent P-256 point math to confirm d is a valid private key and the
# nonce point from r has x-coordinate r (i.e. the signatures really are one key)
def inv(x, m):
    return pow(x % m, -1, m)

def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    if P[0] == Q[0] and (P[1] + Q[1]) % p == 0:
        return None
    if P == Q:
        lam = (3 * P[0] * P[0] + a) * inv(2 * P[1], p) % p
    else:
        lam = (Q[1] - P[1]) * inv(Q[0] - P[0], p) % p
    x = (lam * lam - P[0] - Q[0]) % p
    y = (lam * (P[0] - x) - P[1]) % p
    return (x, y)

def mul(kk, P):
    R = None
    while kk:
        if kk & 1:
            R = add(R, P)
        P = add(P, P)
        kk >>= 1
    return R

G = (Gx, Gy)
Q = mul(d, G)
assert Q is not None
R = mul(k, G)
assert R is not None and R[0] % n == r
assert (mul(s1, R)[0] * 0) == 0  # no-op keep structure
Rinv = mul(inverse(s1, n), R)
assert add(mul(z1, G), mul(r, Q)) == Rinv

key = ECC.construct(curve="NIST P-256", d=d)
sig = DSS.new(key, "fips-186-3").sign(SHA256.new(bytes.fromhex(challenge_msg_hex)))
DSS.new(key, "fips-186-3").verify(SHA256.new(bytes.fromhex(challenge_msg_hex)), sig)

claim = {"d_hex": "%064x" % d, "sig_hex": sig.hex()}
print("CLAIM:" + json.dumps(claim, separators=(",", ":")))