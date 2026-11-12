#!/usr/bin/env python3
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
# ECDSA signature format: r || s, each 32 bytes for P-256
r1 = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:128], 16)
r2 = int(sig2_hex[:64], 16)
s2 = int(sig2_hex[64:128], 16)

# Parse message hashes
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# P-256 curve order
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# Since both signatures use the same nonce k:
# s1 = k^-1 * (z1 + r1*d) mod n
# s2 = k^-1 * (z2 + r2*d) mod n
#
# Rearranging:
# k*s1 = z1 + r1*d mod n
# k*s2 = z2 + r2*d mod n
#
# Subtracting:
# k*(s1 - s2) = (z1 - z2) + (r1 - r2)*d mod n
#
# If r1 == r2 (same nonce means same r):
# k*(s1 - s2) = z1 - z2 mod n
# k = (z1 - z2) * (s1 - s2)^-1 mod n

if r1 == r2:
    # Recover nonce k
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    s_diff_inv = pow(s_diff, -1, n)
    k = (z_diff * s_diff_inv) % n
    
    # Recover private key d from first signature
    # s1 = k^-1 * (z1 + r1*d) mod n
    # s1*k = z1 + r1*d mod n
    # r1*d = s1*k - z1 mod n
    # d = (s1*k - z1) * r1^-1 mod n
    r1_inv = pow(r1, -1, n)
    d = ((s1 * k - z1) % n * r1_inv) % n
else:
    # Different r values - shouldn't happen with same nonce
    # Fall back to general case
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    r_diff = (r1 - r2) % n
    
    # k*(s1 - s2) = (z1 - z2) + (r1 - r2)*d mod n
    # We need another approach - try assuming k is recoverable
    # This shouldn't happen in the standard attack
    raise ValueError("r1 != r2 indicates different nonces")

# Create signature over challenge message with recovered key
key = ECC.construct(curve='NIST P-256', d=d)
hash_obj = SHA256.new(bytes.fromhex(challenge_msg_hex))
signer = DSS.new(key, 'fips-186-3')
signature = signer.sign(hash_obj)

# Format signature as hex (r || s)
sig_hex = signature.hex()

# Format d as 64-char hex
d_hex = format(d, '064x')

# Output claim
claim = {"d_hex": d_hex, "sig_hex": sig_hex}
print(f"CLAIM:{json.dumps(claim)}")