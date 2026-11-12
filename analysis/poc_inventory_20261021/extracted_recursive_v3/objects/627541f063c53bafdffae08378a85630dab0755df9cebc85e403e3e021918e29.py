import sys
import json
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
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

# Parse signatures (r1, s1) and (r2, s2)
# ECDSA signature format: r || s, each 32 bytes
r1 = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:128], 16)
r2 = int(sig2_hex[:64], 16)
s2 = int(sig2_hex[64:128], 16)

# Parse message hashes
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# P-256 curve order
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# Since both signatures used the same nonce k:
# s1 = k^-1 * (z1 + r1*d) mod n
# s2 = k^-1 * (z2 + r2*d) mod n
#
# From these equations:
# s1*k = z1 + r1*d mod n
# s2*k = z2 + r2*d mod n
#
# Subtracting:
# (s1 - s2)*k = (z1 - z2) + (r1 - r2)*d mod n
#
# If r1 == r2 (same nonce means same r):
# (s1 - s2)*k = (z1 - z2) mod n
# k = (z1 - z2) / (s1 - s2) mod n

# Compute k
ds = (s1 - s2) % n
dz = (z1 - z2) % n
ds_inv = pow(ds, -1, n)
k = (dz * ds_inv) % n

# Now recover d from: s1 = k^-1 * (z1 + r1*d) mod n
# s1*k = z1 + r1*d mod n
# r1*d = s1*k - z1 mod n
# d = (s1*k - z1) / r1 mod n

k_inv = pow(k, -1, n)
# Verify: s1 * k should equal z1 + r1*d
# So: r1*d = s1*k - z1
r1_inv = pow(r1, -1, n)
d = ((s1 * k - z1) % n * r1_inv) % n

# Create signature for challenge message
start_ns = time.monotonic_ns()
key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
challenge_hash = SHA256.new(bytes.fromhex(challenge_msg_hex))
sig = signer.sign(challenge_hash)
end_ns = time.monotonic_ns()

# Format signature as hex
sig_hex = sig.hex()

# Format d as 64-character hex
d_hex = format(d, '064x')

# Output claim
print(f'OPSPAN_NS:{end_ns - start_ns}')
print(f'CLAIM:{{"d_hex": "{d_hex}", "sig_hex": "{sig_hex}"}}')
sys.stdout.flush()