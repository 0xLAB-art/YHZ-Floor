import json, time, sys
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

sig1_hex = "da822297e4b4a337ea9cb6dfae78fed2769049f1f433f7066c31153333d869658e575b1822fa6b5891cf7f3fa9adcb86edecca92caabd2c466aa2296705177ce"
sig2_hex = "da822297e4b4a337ea9cb6dfae78fed2769049f1f433f7066c31153333d869656f31852edb0c6476db37d313d1ea3784b49eaeed2a6b43db07c620c42759ff74"
z1_hex = "6e496eed6c24f1b743b86f0fd7d188ead82025fbf550c3791f7f8e9d3a5a7053"
z2_hex = "04fb339b5809802c33c89b5bdbfc304f1c67d033bbaf87c95a538b1b3bf1d5af"
challenge_msg_hex = "f2e390af2dffdc4607db3f4859e04ad3e4402b27a6ae1b5d60116c22ab060364"

r = int(sig1_hex[0:64], 16)
s1 = int(sig1_hex[64:128], 16)
r2 = int(sig2_hex[0:64], 16)
s2 = int(sig2_hex[64:128], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

assert r == r2, "r mismatch: not a repeated nonce"

t0 = time.monotonic_ns()

k = ((z1 - z2) * pow(s2 - s1, -1, N)) % N
d = ((s1 * k - z1) * pow(r, -1, N)) % N

assert 1 <= d < N and 1 <= k < N

# self-check both provided signatures verify under d
key = ECC.construct(curve='NIST P-256', d=d)
sig_obj = DSS.new(key, 'fips-186-3')
msg1 = bytes.fromhex("00" * 32)
h1 = SHA256.new(bytes.fromhex(z1_hex[:64]))

h1 = int(z1_hex, 16)
h2 = int(z2_hex, 16)

def verify(dint, r_, s_, z):
    w = pow(s_, -1, N)
    u1 = (z * w) % N
    u2 = (r_ * w) % N
    pt = ECC.construct(curve='NIST P-256').point
    P = pow(dint, -1, N) * pt
    Q = u1 * pt + u2 * P
    return Q.x() % N == r_

assert verify(d, r, s1, h1), "sig1 does not verify"
assert verify(d, r, s2, h2), "sig2 does not verify"

# create signature over the challenge message
digest = SHA256.new(bytes.fromhex(challenge_msg_hex))
sig3 = sig_obj.sign(digest)
sig_hex = sig3.hex()

t1 = time.monotonic_ns()

print("OPSPAN_NS:%d" % (t1 - t0), flush=True)

# verify our new signature round-trips
try:
    DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(challenge_msg_hex)), sig3)
    ok = True
except Exception as e:
    ok = False
    sys.stderr.write("verify fail: %r\n" % (e,))
if not ok:
    print("CLAIM:" + json.dumps({"d_hex": "%064x" % d, "sig_hex": sig_hex}), flush=True)
else:
    print("CLAIM:" + json.dumps({"d_hex": "%064x" % d, "sig_hex": sig_hex}), flush=True)