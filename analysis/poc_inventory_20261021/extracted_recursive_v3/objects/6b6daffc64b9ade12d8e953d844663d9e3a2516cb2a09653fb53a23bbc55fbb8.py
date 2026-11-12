import hashlib
import json
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256

def modinv(a, n):
    return pow(a, -1, n)

# Provisioned data
sig1_hex = "1d5ec3d5e01cc79f600375f553ac32e30df09985f2dc3b1b4ea2b0b0d49d8c064b9ad8a439ca4fc96d151f7bfaecfb029eefd9b73bc3d84c52ac305d6274651e"
sig2_hex = "1d5ec3d5e01cc79f600375f553ac32e30df09985f2dc3b1b4ea2b0b0d49d8c06491c7a4146f942bb82f37bb57e6f26d71010f0824ab7f43b406a87c51857800d"
z1_hex = "777a2ac5c96cd94cf474206b9d9fde9eb00d46337b67d06838a677ea9a58cf4a"
z2_hex = "0a2eabfd121bc42717b54d7c262eefbdc0a5d8eee8734c54b47b4f60778057c0"
challenge_msg_hex = "0e3044c18fedda2657d44804ec4f04b0eb676f5e861d1f9fedad5f1fb2ede33b"

# Curve order for NIST P-256
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# Parse signatures
r1 = int.from_bytes(bytes.fromhex(sig1_hex[:64]), 'big')
s1 = int.from_bytes(bytes.fromhex(sig1_hex[64:]), 'big')
r2 = int.from_bytes(bytes.fromhex(sig2_hex[:64]), 'big')
s2 = int.from_bytes(bytes.fromhex(sig2_hex[64:]), 'big')
assert r1 == r2, "r values differ"
r = r1

# Parse message hashes
z1 = int.from_bytes(bytes.fromhex(z1_hex), 'big')
z2 = int.from_bytes(bytes.fromhex(z2_hex), 'big')

# Compute k
k = ((z1 - z2) * modinv((s1 - s2) % n, n)) % n
assert k != 0, "k is zero"

# Compute private key d
d = ((s1 * k - z1) * modinv(r, n)) % n
assert 1 <= d < n, "invalid d"

# Construct private key
priv_key = ECC.construct(curve='p256', d=d)
# Compute signature over challenge message
digest = SHA256.new(bytes.fromhex(challenge_msg_hex)).digest()
r_sig, s_sig = priv_key.sign(digest, hash_algo=None)
# enforce low-s
if s_sig > n // 2:
    s_sig = n - s_sig
sig_hex = r_sig.to_bytes(32, 'big').hex() + s_sig.to_bytes(32, 'big').hex()

# Prepare claim
claim = {"d_hex": format(d, '064x'), "sig_hex": sig_hex}
print("CLAIM:" + json.dumps(claim))