import json, time, sys
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

sig1_hex = "6a0ae257dc938d730d68cc7d285275e9edb53cb4aa1e129cccb3da677fa2261546787ac8bccabb45740076f9e8d378803706727b908d88b159aae84bb8fb7978"
sig2_hex = "6a0ae257dc938d730d68cc7d285275e9edb53cb4aa1e129cccb3da677fa226159dc7dd14b37000010e6ae4ba6f78e1e3b99ec9b11c2f2631dcb901fd518d8527"
z1_hex = "65fb765adddead6320d775b7374b5f20ee1b75bae837ce1454b9c24ceeed3d9f"
z2_hex = "4c638a1196a0af0c7c3c9809555e44353f50dfd70e969f7cf317b8b8af9aa83e"
challenge_msg_hex = "a14119873fe3b53668647c9a81a26dcdcf68f4dc9b4eba9725f2df4fdd0d07ad"

t0 = time.monotonic_ns()

n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

s1 = int(sig1_hex[64:128], 16)
s2 = int(sig2_hex[64:128], 16)
r = int(sig1_hex[0:64], 16)
r2 = int(sig2_hex[0:64], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

assert r == r2, "r mismatch"

# (s1 - s2) * k = (z1 - z2) mod n
ds = (s1 - s2) % n
dz = (z1 - z2) % n
k = (dz * pow(ds, -1, n)) % n
d = ((s1 * k - z1) * pow(r, -1, n)) % n

# cross-check with second signature
assert (s2 * k - z2 - r * d) % n == 0

key = ECC.construct(curve='NIST P-256', d=d)
h = SHA256.new(bytes.fromhex(challenge_msg_hex))
sig = DSS.new(key, 'fips-186-3')
sig_hex = sig.sign(h).hex()

# verify locally
DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(challenge_msg_hex)), bytes.fromhex(sig_hex))

t1 = time.monotonic_ns()
print("OPSPAN_NS:%d" % (t1 - t0))
sys.stdout.flush()
print("CLAIM:" + json.dumps({"d_hex": "%064x" % d, "sig_hex": sig_hex}))
sys.stdout.flush()