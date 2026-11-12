from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import json

# Provisioned material
sig1_hex = "3f2468c1e1122fbd1705d6ccc484b6485dad2fee4bb86d13d2e58d809ac3dddde8e7ada56d89bc6189f062a9b28fc509e2f6a11be13ceb4b6b788028a7efed8a"
sig2_hex = "3f2468c1e1122fbd1705d6ccc484b6485dad2fee4bb86d13d2e58d809ac3ddddd58d532da27d8991826e797a15951b0ca304bd85d039084746068e9cca2e405b"
z1_hex = "a4b8c9803f9bd73a04fa1bfa86152ee67e4d74afa36170fd424a28a391cc9538"
z2_hex = "59466c75bd9f20735bb4bfad06fe331255af7377b7dad7a4e952e8c233125659"
challenge_msg_hex = "ec655ed972fe26d95d7393793331f3f03e36d4c322154bc3d9c9cd9e39f49b60"

# Parse signatures (r||s, 64 bytes each)
r1 = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:], 16)
r2 = int(sig2_hex[:64], 16)
s2 = int(sig2_hex[64:], 16)

# Parse message hashes
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# NIST P-256 curve order
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

# Verify r1 == r2 (same nonce)
assert r1 == r2, "r values differ"
r = r1

# Recover k: k = (z1 - z2) * inverse(s1 - s2, n) mod n
k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n

# Recover d: d = (s1*k - z1) * inverse(r, n) mod n
d = ((s1 * k - z1) * pow(r, -1, n)) % n

# Verify with second signature: s2*k should equal z2 + r*d mod n
assert (s2 * k) % n == (z2 + r * d) % n, "Verification failed"

# Create signature over challenge message
d_hex = format(d, '064x')
key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
h = SHA256.new(bytes.fromhex(challenge_msg_hex))
sig = signer.sign(h)
sig_hex = sig.hex()

print(f"d_hex: {d_hex}")
print(f"sig_hex: {sig_hex}")

result = {"d_hex": d_hex, "sig_hex": sig_hex}
print(f"CLAIM:{json.dumps(result)}")