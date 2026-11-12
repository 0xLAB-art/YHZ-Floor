from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
import json, time

sig1_hex = "185a129a91a75146efcbd13d463e7bda24615b9234b78b6833809ef690da000e98bee0860fa3ae0bc79570ffb3abf3c52de054b9ea493858df50c3f41d7ec2f3"
sig2_hex = "185a129a91a75146efcbd13d463e7bda24615b9234b78b6833809ef690da000e17ea8309bc2c71a23b2814fa63643ad1669a68d5fdb5930f15e8758b51672e6a"
z1_hex = "a060f22485da3c249e01337c4ebd424873cd47f486ebfa3beae08ad318bea940"
z2_hex = "cf3093426b890e6551d6ae0f3bc269470949c4a529aa7367ee96229c295319c8"
challenge_msg_hex = "1c596c3263c96b8b4e8a3aa6c75c0c1b3161a9af0b689b58c58151461206fe3e"

start = time.monotonic_ns()

p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a = p - 3
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
Gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
Gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5

r1 = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:], 16)
r2 = int(sig2_hex[:64], 16)
s2 = int(sig2_hex[64:], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)
assert r1 == r2 and r1 != 0

def inv(x, m):
    return pow(int(x), -1, m)

def pt_add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = int(P[0]), int(P[1])
    x2, y2 = int(Q[0]), int(Q[1])
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if x1 == x2 and y1 == y2:
        lam = (3 * x1 * x1 + a) * inv(2 * y1, p) % p
    else:
        lam = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def pt_mul(k, P):
    R = None
    Q = P
    k = int(k) % n
    while k:
        if k & 1:
            R = pt_add(R, Q)
        Q = pt_add(Q, Q)
        k >>= 1
    return R

G = (Gx, Gy)

def rx(k):
    R = pt_mul(k, G)
    if R is None:
        return None
    return R[0] % n

d = None
for ss1 in (s1, n - s1):
    for ss2 in (s2, n - s2):
        ds = (ss1 - ss2) % n
        if ds == 0:
            continue
        k = (z1 - z2) * inv(ds, n) % n
        if k == 0:
            continue
        dd = (ss1 * k - z1) * inv(r1, n) % n
        if dd == 0:
            continue
        if rx(k) != r1:
            continue
        k2 = (z2 + r1 * dd) * inv(ss2, n) % n
        if rx(k2) != r1:
            continue
        d = dd
        break
    if d is not None:
        break

assert d is not None, "recovery failed"
opspan = time.monotonic_ns() - start

d_hex = format(d, '064x')
key = ECC.construct(curve='NIST P-256', d=d)
h = SHA256.new(bytes.fromhex(challenge_msg_hex))
signer = DSS.new(key, 'fips-186-3')
sig = signer.sign(h)
sig_hex = sig.hex()

print(f"OPSPAN_NS:{opspan}", flush=True)
print("CLAIM:" + json.dumps({"d_hex": d_hex, "sig_hex": sig_hex}), flush=True)