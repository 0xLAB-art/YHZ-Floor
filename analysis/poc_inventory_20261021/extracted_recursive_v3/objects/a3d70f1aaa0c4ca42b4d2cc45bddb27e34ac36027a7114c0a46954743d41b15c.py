from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

# Provisioned material
sig1_hex = "c62c04b05f6ae0e1f942f9eed9216188daeef76defed460b2326b22a02f49b1588dc7aa0a652976eee6405d5237aab4b9ecf79a5e11eb53d35fc6febb2281d4"
sig2_hex = "c62c04b05f6ae0e1f942f9eed9216188daeef76defed460b2326b22a02f49b104453ac7406f1c730295b9bea539869045d051073703f40d45efa1d5a66ee34c"
z1_hex = "fe7d3130e3936f8d95e4dec8577d34d50d245bb61999ef90a4d1ca2d930198bc"
z2_hex = "f3efd4deba6bf7c793298e765ac4bd03d64a1707ead1481deabd76c3d4a9c3de"
challenge_msg_hex = "9782e2b33303fe486db32836aac8e6de6c92ed49e0e51bad22442828fa61d53c"

# Parse signatures
sig1 = bytes.fromhex(sig1_hex)
sig2 = bytes.fromhex(sig2_hex)

r1 = int.from_bytes(sig1[:32], 'big')
s1 = int.from_bytes(sig1[32:], 'big')
r2 = int.from_bytes(sig2[:32], 'big')
s2 = int.from_bytes(sig2[32:], 'big')

z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# NIST P-256 curve order
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

# Recover nonce k
# s1 - s2 = k^(-1) * (z1 - z2) mod n
# k = (z1 - z2) * inverse(s1 - s2, n) mod n
k = (z1 - z2) * pow(s1 - s2, -1, n) % n

# Recover private key d
# s1 * k = z1 + r1 * d mod n
# d = (s1 * k - z1) * inverse(r1, n) mod n
d = (s1 * k - z1) * pow(r1, -1, n) % n

# Create signature for challenge message
key = ECC.construct(curve='NIST P-256', d=d)
h = SHA256.new(bytes.fromhex(challenge_msg_hex))
signer = DSS.new(key, 'fips-186-3')
signature = signer.sign(h)
sig_hex = signature.hex()

print(f"d_hex: {d:064x}")
print(f"sig_hex: {sig_hex}")

# Output claim
import json
claim = {"d_hex": f"{d:064x}", "sig_hex": sig_hex}
print(f"CLAIM:{json.dumps(claim)}")