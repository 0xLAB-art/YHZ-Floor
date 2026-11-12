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

# NIST P-256 parameters
p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a = -3 % p
b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
Gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
Gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5

r1 = int(sig1_hex[:64], 16); s1 = int(sig1_hex[64:], 16)
r2 = int(sig2_hex[:64], 16); s2 = int(sig2_hex[64:], 16)
z1 = int(z1_hex, 16); z2 = int(z2_hex, 16)
assert r1 == r2

inv = lambda x: pow(x, -1, n)

d = None
for ss1 in (s1, n - s1):
    for ss2 in (s2, n - s2):
        if (ss1 - ss2) % n == 0:
            continue
        k = ((z1 - z2) * inv((ss1 - ss2) % n)) % n
        if k == 0:
            continue
        dd = ((ss1 * k - z1) * inv(r1)) % n
        if dd == 0:
            continue
        # verify: compute point k*G and check signature eq
        # d*G == s^{-1}(z*G + r*P) style check via r == x(k*G)
        # simplest: check ECDSA verify relation with recovered d
        try:
            key = ECC.construct(curve='NIST P-256', d=dd)
            # verify sig1
            h = SHA256.new(bytes.fromhex(z1_hex) if False else b'')
        except Exception:
            continue
        # explicit verification of sig1 under dd
        Px = key.pointQ.x; Py = key.pointQ.y
        u1 = (z1 * inv(ss1)) % n
        u2 = (r1 * inv(ss1)) % n
        # point = u1*G + u2*P
        def pt_add(P, Q):
            if P is None: return Q
            if Q is None: return P
            x1, y1 = P; x2, y2 = Q
            if x1 == x2 and (y1 + y2) % p == 0: return None
            if P == Q:
                lam = (3 * x1 * x1 + a) * inv_mod(2 * y1, p) % p
            else:
                lam = (y2 - y1) * inv_mod(x2 - x1, p) % p
            x3 = (lam * lam - x1 - x2) % p
            y3 = (lam * (x1 - x3) - y1) % p
            return (x3, y3)
        def inv_mod(x, m):
            return pow(x, -1, m)
        def pt_mul(k_, P):
            R = None; Q = P
            while k_:
                if k_ & 1: R = pt_add(R, Q)
                Q = pt_add(Q, Q); k_ >>= 1
            return R
        G = (Gx, Gy)
        Pt = pt_add(pt_mul(u1, G), pt_mul(u2, (Px, Py)))
        if Pt is not None and Pt[0] % n == r1:
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

print(f"OPSPAN_NS:{opspan}")
print("CLAIM:" + json.dumps({"d_hex": d_hex, "sig_hex": sig_hex}))