import sys
import json
import hashlib
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

# Provisioned material
sig1_hex = "e59d7325231bb9608e3410959c33ffacd314c8d2eccabd93756259bc8791c4b4c56b2472a9d8845a13afa4754c922d6d64e3275050100b7307d99c20632bbbf8"
sig2_hex = "e59d7325231bb9608e3410959c33ffacd314c8d2eccabd93756259bc8791c4b4bd121d9573087779475dbc1a187d03463b1cce0324d0c05fc5d4a98d5f8cdc2b"
z1_hex = "e0737c29123f38f33eb7eee0588bbb9be1b46f4fc4a7a433169e39061db718ca"
z2_hex = "920e62169e3abcaaa462c2ef2060e877d3369360dc8255bd87c3b43fce8be258"
challenge_msg_hex = "9db55510d789e1eefdbfaf032f831833642f36dfdeb075bdd1fe416825da26ad"

# NIST P-256 curve order
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# Parse signatures (r || s, each 32 bytes)
sig1 = bytes.fromhex(sig1_hex)
sig2 = bytes.fromhex(sig2_hex)

r1 = int.from_bytes(sig1[:32], 'big')
s1 = int.from_bytes(sig1[32:], 'big')
r2 = int.from_bytes(sig2[:32], 'big')
s2 = int.from_bytes(sig2[32:], 'big')

# Verify r values are the same (same nonce k)
assert r1 == r2, f"r values differ: {r1} vs {r2}"
r = r1

# Parse message digests
z1 = int.from_bytes(bytes.fromhex(z1_hex), 'big')
z2 = int.from_bytes(bytes.fromhex(z2_hex), 'big')

# Repeated nonce attack:
# s1 = k^-1 * (z1 + r*d) mod n
# s2 = k^-1 * (z2 + r*d) mod n
# s1 - s2 = k^-1 * (z1 - z2) mod n
# k = (z1 - z2) * (s1 - s2)^-1 mod n
# d = (s1 * k - z1) * r^-1 mod n

s1_minus_s2 = (s1 - s2) % n
z1_minus_z2 = (z1 - z2) % n

# Compute modular inverse
k = (z1_minus_z2 * pow(s1_minus_s2, -1, n)) % n
d = ((s1 * k - z1) * pow(r, -1, n)) % n

print(f"Recovered d: {d:064x}", file=sys.stderr)

# Verify by signing challenge message
challenge_msg = bytes.fromhex(challenge_msg_hex)
z_challenge = int.from_bytes(hashlib.sha256(challenge_msg).digest(), 'big')

# Create ECC key from recovered private scalar
key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
signature = signer.sign(SHA256.new(challenge_msg))
sig_hex = signature.hex()

print(f"Signature: {sig_hex}", file=sys.stderr)

# Verify the signature verifies
verifier = DSS.new(key.public_key(), 'fips-186-3')
try:
    verifier.verify(SHA256.new(challenge_msg), signature)
    print("Signature verification: PASSED", file=sys.stderr)
except ValueError:
    print("Signature verification: FAILED", file=sys.stderr)

# Output claim
claim = {
    "d_hex": f"{d:064x}",
    "sig_hex": sig_hex
}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()