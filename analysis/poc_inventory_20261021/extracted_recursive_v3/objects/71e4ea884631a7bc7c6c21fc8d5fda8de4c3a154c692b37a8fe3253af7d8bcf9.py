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

# Since same nonce k was used for both signatures:
# s1 = k^-1 * (z1 + r1*d) mod n
# s2 = k^-1 * (z2 + r2*d) mod n
#
# If r1 == r2 (which should be the case with same nonce):
# s1 - s2 = k^-1 * (z1 - z2) mod n
# k = (z1 - z2) / (s1 - s2) mod n
#
# Then:
# d = (s1*k - z1) / r1 mod n

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm"""
    return pow(a, -1, m)

# Recover nonce k
k = ((z1 - z2) * modinv(s1 - s2, n)) % n

# Recover private key d
d = ((s1 * k - z1) * modinv(r1, n)) % n

# Verify our recovered key works by creating signature on challenge message
key = ECC.construct(curve='P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
hash_obj = SHA256.new(bytes.fromhex(challenge_msg_hex))
signature = signer.sign(hash_obj)

# Convert signature to hex
sig_hex = signature.hex()

# Format d as 64 hex chars (32 bytes)
d_hex = format(d, '064x')

# Output claim
claim = {"d_hex": d_hex, "sig_hex": sig_hex}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()