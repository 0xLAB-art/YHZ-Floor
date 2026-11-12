import json
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Signature import DSS

CURVE = ECC._curves["NIST P-256"]
group_order = CURVE.order
G = CURVE.generator

sig1_hex = "a4747264e8b54d5760a7e721be773f31266482cdcd7eb83425bda7368021ccf9ccd2e22e8e74f36ade45754c0fb868c0562b035c25cf44f67888ecd050299136"
sig2_hex = "a4747264e8b54d5760a7e721be773f31266482cdcd7eb83425bda7368021ccf9d4780f3171f8ce3a73354fea00748ef55b0bcee914819e19c70576ec3328fd8a"
z1_hex = "7cbd67c50ebeaa59b8bd618bbdc04b647f08cd322e5e6c80db3b438538b1c714"
z2_hex = "535c6d9cbb19b561837c495131dfb18d814577533ad4e0c9c4875271973e3f1e"
challenge_msg_hex = "ba9468215a1c2785ded12b386f13281f5c16a952374167f58962702d05dea6e5"

def chunks(h):
    b = bytes.fromhex(h)
    r = int.from_bytes(b[:32], "big")
    s = int.from_bytes(b[32:64], "big")
    return r, s

r1, s1 = chunks(sig1_hex)
r2, s2 = chunks(sig2_hex)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)
assert r1 == r2
r = r1
n = group_order

k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n
d = ((s1 * k - z1) * pow(r, -1, n)) % n

# self-verify
for sig, z in ((sig1_hex, z1), (sig2_hex, z2)):
    rr, ss = chunks(sig)
    w = pow(ss, -1, n)
    u1 = z * w % n
    u2 = rr * w % n
    pt = u1 * G + u2 * ECC.construct(curve="NIST P-256", point=u1 * G + u2 * (G * (rr * pow(rr, -1, n) % n) * 0 + G))  # unused

key = ECC.construct(curve="NIST P-256", d=d)
h = SHA256.new(bytes.fromhex(challenge_msg_hex))
sig3 = DSS.new(key, "fips-186-3").sign(h)
DSS.new(key, "fips-186-3").verify(SHA256.new(bytes.fromhex(challenge_msg_hex)), sig3)
print("CLAIM:" + json.dumps({"d_hex": "%064x" % d, "sig_hex": sig3.hex()}, separators=(",", ":")))