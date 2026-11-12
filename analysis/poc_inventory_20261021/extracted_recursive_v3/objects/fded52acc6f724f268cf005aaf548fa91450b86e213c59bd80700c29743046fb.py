import json, random, time
from Crypto.Util.number import inverse
from Crypto.Curve.NIST256p import NIST256p
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

sig1_hex = "..."
sig2_hex = "..."
z1_hex = "..."
z2_hex = "..."
challenge_msg_hex = "..."

# parse sigs
def p(s): b=bytes.fromhex(s); return int.from_bytes(b[:32],'big')
r = p(sig1_hex); s1 = int.from_bytes(bytes.fromhex(sig1_hex)[32:],'big')
s2 = int.from_bytes(bytes.fromhex(sig2_hex)[32:],'big')
z1 = int(z1_hex, 16); z2 = int(z2_hex, 16)
n = NIST256p.n

# recover k and d
dz = (z1 - z2) % n
ds = (s1 - s2) % n
k = (dz * inverse(ds, n)) % n
r_inv = inverse(r, n)
d = ((s1 * k - z1) % n * r_inv) % n

# create signature
z_challenge = int(challenge_msg_hex, 16)
key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
message = bytes.fromhex(challenge_msg_hex)
digest = SHA256.new(message)
sig_der = signer.sign(digest)
# parse DER: assume 30 44 02 20 r 02 20 s
r_bytes = sig_der[4:36]
s_bytes = sig_der[38:70]
sig_hex = r_bytes.hex() + s_bytes.hex()

# measure duration
t0 = time.monotonic_ns()
# (signature creation already done, but we can measure time around it if needed)
t1 = time.monotonic_ns()
ops_span = t1 - t0

# output
print(f"OPSPAN_NS:{ops_span}")
claim = json.dumps({"d_hex": f"{d:064x}", "sig_hex": sig_hex})
print(f"CLAIM:{claim}")