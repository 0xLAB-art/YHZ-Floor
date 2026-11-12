from Crypto.Hash import SHA256
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC

# Provisioned material
sig1_hex = "6b896468a6b0de8b333a030bab4b7c8dc9ee9b1584be01e385263234eb13c8de0167be508aec3bbdb439fdac5e4bba85f57885c08ccdc7b5dcc6d1eb6a041d3d"
sig2_hex = "6b896468a6b0de8b333a030bab4b7c8dc9ee9b1584be01e385263234eb13c8dea43de19cf181ed4ab1ecd905841bd8052a954bf24d525b97baf3144caaa8a148"
z1_hex = "8d3049b15b96f37fa00f8089b6a23c6a2ca535356a8fd03922e40f7c8d8ffdad"
z2_hex = "b32fbe7ae3ece2a7f2a7818dd63e2b5a37ffaff5ec0d47af488293b4f6ac189a"
challenge_msg_hex = "a7314c6e47448ae2575d6333fbf8f5e1f318b7e8c1eb9d7c0167b74539f7c7f0"

# Parse signatures
r1 = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:], 16)
r2 = int(sig2_hex[:64], 16)
s2 = int(sig2_hex[64:], 16)

z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# NIST P-256 curve order
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

# Verify r values match (same nonce means same r)
assert r1 == r2, f"r values differ: {r1} vs {r2}"
r = r1

# Recover k: k = (z1 - z2) * inverse(s1 - s2, n) mod n
k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n

# Recover d: d = (s1*k - z1) * inverse(r, n) mod n
d = ((s1 * k - z1) * pow(r, -1, n)) % n

print(f"Recovered d: {format(d, '064x')}")

# Create signature over challenge message
key = ECC.construct(curve='NIST P-256', d=d)
challenge_msg = bytes.fromhex(challenge_msg_hex)
h = SHA256.new(challenge_msg)
signer = DSS.new(key, 'fips-186-3')
sig = signer.sign(h)
sig_hex = sig.hex()

print(f"Signature: {sig_hex}")

# Verify
verifier = DSS.new(key.public_key(), 'fips-186-3')
try:
    verifier.verify(SHA256.new(challenge_msg), bytes.fromhex(sig_hex))
    print("Signature verified!")
except:
    print("Signature verification failed!")

print(f"CLAIM: {{\"d_hex\": \"{format(d, '064x')}\", \"sig_hex\": \"{sig_hex}\"}}")