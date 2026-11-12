import json
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Signature import DSS

P = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
A  = P - 3
B  = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
GX = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
GY = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
N  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
G  = (GX, GY)

def pt_add(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    x1, y1 = p1; x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0: return None
    if p1 == p2:
        l = (3 * x1 * x1 + A) * pow(2 * y1, -1, P) % P
    else:
        l = (y2 - y1) * pow(x2 - x1, -1, P) % P
    x3 = (l * l - x1 - x2) % P
    return (x3, (l * (x1 - x3) - y1) % P)

def pt_mul(k, p=G):
    r = None
    a = p
    k %= N
    while k:
        if k & 1: r = pt_add(r, a)
        a = pt_add(a, a)
        k >>= 1
    return r

def split(sig_hex):
    b = bytes.fromhex(sig_hex)
    return int.from_bytes(b[:32], 'big'), int.from_bytes(b[32:64], 'big')

sig1_hex = "a4747264e8b54d5760a7e721be773f31266482cdcd7eb83425bda7368021ccf9ccd2e22e8e74f36ade45754c0fb868c0562b035c25cf44f67888ecd050299136"
sig2_hex = "a4747264e8b54d5760a7e721be773f31266482cdcd7eb83425bda7368021ccf9d4780f3171f8ce3a73354fea00748ef55b0bcee914819e19c70576ec3328fd8a"
z1_hex = "7cbd67c50ebeaa59b8bd618bbdc04b647f08cd322e5e6c80db3b438538b1c714"
z2_hex = "535c6d9cbb19b561837c495131dfb18d814577533ad4e0c9c4875271973e3f1e"
challenge_msg_hex = "ba9468215a1c2785ded12b386f13281f5c16a952374167f58962702f05dea6e5"

r1, s1 = split(sig1_hex)
r2, s2 = split(sig2_hex)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)
assert r1 == r2, 'r mismatch'
r = r1

k = (z1 - z2) * pow((s1 - s2) % N, -1, N) % N
d = ((s1 * k - z1) * pow(r, -1, N)) % N

Q = pt_mul(d)
for sig_hex, z in ((sig1_hex, z1), (sig2_hex, z2)):
    rr, ss = split(sig_hex)
    w = pow(ss, -1, N)
    R = pt_add(pt_mul(z * w % N), pt_mul(rr * w % N, Q))
    assert R is not None and R[0] % N == rr, 'self-verify failed'

key = ECC.construct(curve='NIST P-256', d=d)
msg = SHA256.new(bytes.fromhex(challenge_msg_hex))
sig3 = DSS.new(key, 'fips-186-3').sign(msg)
DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(challenge_msg_hex)), sig3)
print("CLAIM:" + json.dumps({"d_hex": "%064x" % d, "sig_hex": sig3.hex()}, separators=(',', ':')))