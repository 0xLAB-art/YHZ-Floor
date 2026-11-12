import json
import sys
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

# Provisioned material
sig1_hex = "5516242128f0aed4b6191c10d07f4576663e6fef7e16433a94748e71f5914e6077ca386d3375bc29a4445e40419ad71abe8f68b1638b4c37a9259f7fbbec18aa"
sig2_hex = "5516242128f0aed4b6191c10d07f4576663e6fef7e16433a94748e71f5914e6040c6920c98778545920f4a5f4b0d9d27fb059af3caa2c138dd2b50c4abb910f3"
z1_hex = "a3079fd7246a4c333d41347813faa8f1d795cb04e322ae26e0af562080dd2a05"
z2_hex = "131870cb564ee53f31a7155b52bea6b0077a4313a7a514fe48cb288c65ed3c04"
challenge_msg_hex = "4440fec3e08bf2ff1624938783cf1857e69948fffa9a779dd908bd411ff48234"

# NIST P-256 curve order
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# Parse signatures (64 bytes = 32 bytes r || 32 bytes s)
sig1 = bytes.fromhex(sig1_hex)
sig2 = bytes.fromhex(sig2_hex)

r1 = int.from_bytes(sig1[:32], 'big')
s1 = int.from_bytes(sig1[32:], 'big')
r2 = int.from_bytes(sig2[:32], 'big')
s2 = int.from_bytes(sig2[32:], 'big')

# r should be the same for both signatures (same nonce k)
assert r1 == r2, f"r values differ: {r1} != {r2}"
r = r1

z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# Recover k: k = (z1 - z2) * (s1 - s2)^(-1) mod n
s_diff = (s1 - s2) % n
z_diff = (z1 - z2) % n
k = (z_diff * pow(s_diff, -1, n)) % n

# Recover d: d = (s1 * k - z1) * r^(-1) mod n
d = ((s1 * k - z1) % n * pow(r, -1, n)) % n

# Verify d works with second signature too
d_check = ((s2 * k - z2) % n * pow(r, -1, n)) % n
assert d == d_check, "Private key mismatch"

# Create key and sign challenge message
key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
challenge_hash = SHA256.new(bytes.fromhex(challenge_msg_hex))
sig = signer.sign(challenge_hash)
sig_hex = sig.hex()

# Output claim
d_hex = format(d, '064x')
claim = {"d_hex": d_hex, "sig_hex": sig_hex}
print(f"CLAIM:{json.dumps(claim)}")