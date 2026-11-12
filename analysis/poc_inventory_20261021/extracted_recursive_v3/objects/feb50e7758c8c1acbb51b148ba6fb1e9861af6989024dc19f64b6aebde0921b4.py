import sys
import json
import hashlib
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

# Provisioned material
sig1_hex = "22fdf0a36defbcf3da03e5fdb085eb93de568f8fcece6a7bcc6e2c0d40f0af85b02aa2431835b93c9c01bff16c9e79297b73d70569037d8e244a3236e30a89a3"
sig2_hex = "22fdf0a36defbcf3da03e5fdb085eb93de568f8fcece6a7bcc6e2c0d40f0af85a7f9369bcf8eb5e87f7304c931fb6859d3ea61ee73ecf3ea9a95b4e34e8f92f0"
z1_hex = "0c721dd5349fdd03705139d26397cd3b3f2732732a89404b8b9e20f80c637176"
z2_hex = "c5334e7fd39ad7e564eda73459571c53759a810782a8acc529ca620050d7585e"
challenge_msg_hex = "2b871c678bf261e8ea5009760f2d90375ee1a1504ced28d4e1913b50376c544d"

# NIST P-256 curve order
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# Parse signatures (64 bytes = 32 bytes r || 32 bytes s)
sig1 = bytes.fromhex(sig1_hex)
sig2 = bytes.fromhex(sig2_hex)

r = int.from_bytes(sig1[:32], 'big')
s1 = int.from_bytes(sig1[32:], 'big')
s2 = int.from_bytes(sig2[32:], 'big')

z1 = int.from_bytes(bytes.fromhex(z1_hex), 'big')
z2 = int.from_bytes(bytes.fromhex(z2_hex), 'big')

# Verify r is the same for both signatures
r2 = int.from_bytes(sig2[:32], 'big')
assert r == r2, f"r mismatch: {r} != {r2}"

# Recover k: k = (z1 - z2) * (s1 - s2)^-1 mod n
z_diff = (z1 - z2) % n
s_diff = (s1 - s2) % n
s_diff_inv = pow(s_diff, -1, n)
k = (z_diff * s_diff_inv) % n

# Recover d: d = (s1 * k - z1) * r^-1 mod n
r_inv = pow(r, -1, n)
d = ((s1 * k - z1) % n * r_inv) % n

# Verify with second signature
d2 = ((s2 * k - z2) % n * r_inv) % n
assert d == d2, f"d mismatch: {d} != {d2}"

# Create signature for challenge message
challenge_msg = bytes.fromhex(challenge_msg_hex)
z_challenge = int.from_bytes(hashlib.sha256(challenge_msg).digest(), 'big')

# Sign with recovered private key
key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
sig = signer.sign(SHA256.new(challenge_msg))
sig_hex = sig.hex()

d_hex = format(d, '064x')

print(f"CLAIM:{{\"d_hex\": \"{d_hex}\", \"sig_hex\": \"{sig_hex}\"}}")