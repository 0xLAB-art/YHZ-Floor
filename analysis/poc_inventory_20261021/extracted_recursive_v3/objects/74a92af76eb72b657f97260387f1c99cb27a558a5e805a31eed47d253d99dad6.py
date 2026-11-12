import sys
import json
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

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
r1 = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:128], 16)
r2 = int(sig2_hex[:64], 16)
s2 = int(sig2_hex[64:128], 16)

# Parse message hashes
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# NIST P-256 order
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# Recover nonce k from repeated nonce attack
# s1 = k^-1 * (z1 + r1*d) mod n
# s2 = k^-1 * (z2 + r2*d) mod n
# Since r1 == r2 (same nonce k gives same r):
# s1 - s2 = k^-1 * (z1 - z2) mod n
# k = (z1 - z2) / (s1 - s2) mod n

k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n

# Recover private key d
# s1 = k^-1 * (z1 + r1*d) mod n
# d = (s1*k - z1) / r1 mod n

d = ((s1 * k - z1) * pow(r1, -1, n)) % n

# Format d as 64-char hex
d_hex = format(d, '064x')

# Sign the challenge message
key = ECC.construct(curve='NIST P-256', d=d)
hash_obj = SHA256.new(bytes.fromhex(challenge_msg_hex))
signer = DSS.new(key, 'fips-186-3')
sig = signer.sign(hash_obj)
sig_hex = sig.hex()

# Output claim
claim = {"d_hex": d_hex, "sig_hex": sig_hex}
print(f"CLAIM:{json.dumps(claim)}")