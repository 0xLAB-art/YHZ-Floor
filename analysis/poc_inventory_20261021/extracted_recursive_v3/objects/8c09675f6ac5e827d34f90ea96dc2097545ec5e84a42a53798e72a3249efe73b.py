import sys
import json
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
import time

# Read task instance
with open(sys.argv[1], 'r') as f:
    task = json.load(f)

public_input = task['public_input']
sig1_hex = public_input['sig1_hex']
sig2_hex = public_input['sig2_hex']
z1_hex = public_input['z1_hex']
z2_hex = public_input['z2_hex']
challenge_msg_hex = public_input['challenge_msg_hex']

# ECDSA signature format: r || s (each 32 bytes for P-256)
r1 = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:], 16)
r2 = int(sig2_hex[:64], 16)
s2 = int(sig2_hex[64:], 16)

z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# P-256 curve order
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

# Same nonce k used for both signatures means r1 == r2
# ECDSA equations:
# s1 = k^-1 * (z1 + r1*d) mod n
# s2 = k^-1 * (z2 + r2*d) mod n
#
# Since r1 == r2 = r:
# s1 - s2 = k^-1 * (z1 - z2) mod n
# k = (z1 - z2) / (s1 - s2) mod n

r = r1  # Should equal r2

# Recover nonce k
ds = (s1 - s2) % n
dz = (z1 - z2) % n
ds_inv = pow(ds, -1, n)
k = (dz * ds_inv) % n

# Recover private key d from first signature
# s1 = k^-1 * (z1 + r*d) mod n
# s1 * k = z1 + r*d mod n
# d = (s1*k - z1) / r mod n

sk = (s1 * k) % n
r_inv = pow(r, -1, n)
d = ((sk - z1) % n * r_inv) % n

# Format d as 64-char hex
d_hex = format(d, '064x')

# Sign challenge message with recovered key
start_ns = time.monotonic_ns()
key = ECC.construct(curve='P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
h = SHA256.new(bytes.fromhex(challenge_msg_hex))
signature = signer.sign(h)
end_ns = time.monotonic_ns()

# Convert signature to hex
sig_hex = signature.hex()

# Output claim
print(f'CLAIM:{{"d_hex": "{d_hex}", "sig_hex": "{sig_hex}"}}')
print(f'OPSPAN_NS:{end_ns - start_ns}')
sys.stdout.flush()