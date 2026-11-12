import json, sys, time
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Signature import DSS

SIG1_HEX = "b52696f20fa96e9d0025a3beacb585bbdd46552ca9cbb1006b151aca638637ac80678f22d5117e2584b5e28dd69611f48afa81443b6ebdb8f4a30c51fac16bfe"
SIG2_HEX = "b52696f20fa96e9d0025a3beacb585bbdd46552ca9cbb1006b151aca638637ac7129b57313c2c7d2c08aa3732e0d5483331e2870d84fb44472f547d9755f083a"
Z1_HEX = "440b597f394dcb3accf74c192abc6f67e490040b307a29a71b3f6a3a9877bd07"
Z2_HEX = "71831443c8a46c9df7768422b4229c0efb338aab63551a444b91cfb69cc17921"
CHALLENGE_MSG_HEX = "d2ed7828251892c36b4e1dfa514386b52451e8629e0ee6632779cf6b1f223d19"

N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

sig1 = bytes.fromhex(SIG1_HEX)
sig2 = bytes.fromhex(SIG2_HEX)
r1 = int.from_bytes(sig1[0:32], "big")
s1 = int.from_bytes(sig1[32:64], "big")
r2 = int.from_bytes(sig2[0:32], "big")
s2 = int.from_bytes(sig2[32:64], "big")
z1 = int(Z1_HEX, 16)
z2 = int(Z2_HEX, 16)

t_start = time.monotonic_ns()

assert r1 == r2, "nonce reuse must share r"

# k reuse: s_i = k^-1 (z_i + r*d) mod n
k = ((z1 - z2) * pow(s1 - s2, -1, N)) % N
d = ((s1 * k - z1) * pow(r1, -1, N)) % N

assert (s1 * k - (z1 + r1 * d)) % N == 0
assert (s2 * k - (z2 + r2 * d)) % N == 0

d_hex = "%064x" % d

key = ECC.construct(curve="NIST P-256", d=d)
msg = bytes.fromhex(CHALLENGE_MSG_HEX)
signer = DSS.new(key, "fips-186-3")
raw = signer.sign(SHA256.new(msg))

# pycryptodome 'fips-186-3' returns raw r||s (64 bytes); normalize to low-s just in case
assert len(raw) == 64, len(raw)
rr = int.from_bytes(raw[0:32], "big")
ss = int.from_bytes(raw[32:64], "big")
if ss > N // 2:
    ss = N - ss
sig_bytes = rr.to_bytes(32, "big") + ss.to_bytes(32, "big")

# self-verify: re-sign/verify round trip
try:
    DSS.new(key, "fips-186-3").verify(SHA256.new(msg), sig_bytes)
    ok = True
except Exception as e:
    ok = False
    print("self-verify failed: %r" % (e,), file=sys.stderr)

# also verify with 'der' mode by encoding manually
def der_int(x):
    b = x.to_bytes(32, "big").lstrip(b"\x00") or b"\x00"
    if b[0] & 0x80:
        b = b"\x00" + b
    return b"\x02" + bytes([len(b)]) + b

body = der_int(rr) + der_int(ss)
der = b"\x30" + bytes([len(body)]) + body
try:
    DSS.new(key, "fips-186-3", mode="der").verify(SHA256.new(msg), der)
    ok_der = True
except Exception as e:
    ok_der = False
    print("der self-verify failed: %r" % (e,), file=sys.stderr)

opspan = time.monotonic_ns() - t_start
print("d=%s ok=%s ok_der=%s" % (d_hex, ok, ok_der), file=sys.stderr)

claim = {"d_hex": d_hex, "sig_hex": sig_bytes.hex()}
print("CLAIM:" + json.dumps(claim, separators=(",", ":")))
print("OPSPAN_NS:%d" % opspan)
sys.stdout.flush()