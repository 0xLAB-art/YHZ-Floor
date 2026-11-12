import sys
import json
from hashlib import sha256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

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
# ECDSA signature is typically (r, s) each 32 bytes for P-256
r1 = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:128], 16)
r2 = int(sig2_hex[:64], 16)
s2 = int(sig2_hex[64:128], 16)

# Parse message hashes
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# P-256 curve order
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

# Since both signatures use the same nonce k:
# s1 = k^(-1) * (z1 + r1 * d) mod n
# s2 = k^(-1) * (z2 + r2 * d) mod n
#
# If r1 == r2 (same r means same nonce was used):
# s1 - s2 = k^(-1) * (z1 - z2) mod n
# k = (z1 - z2) / (s1 - s2) mod n
#
# Then: d = (s1 * k - z1) / r1 mod n

# Calculate k
s_diff = (s1 - s2) % n
z_diff = (z1 - z2) % n
s_diff_inv = pow(s_diff, -1, n)
k = (z_diff * s_diff_inv) % n

# Calculate private key d
k_inv = pow(k, -1, n)
d = ((s1 * k - z1) * pow(r1, -1, n)) % n

# Format d as 64-character lowercase hex
d_hex = format(d, '064x')

# Create signature over challenge message
key = ECC.construct(curve='P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
challenge_hash = SHA256.new(bytes.fromhex(challenge_msg_hex))
signature = signer.sign(challenge_hash)
sig_hex = signature.hex()

# Output claim
claim = {"d_hex": d_hex, "sig_hex": sig_hex}
print(f"CLAIM:{json.dumps(claim)}")