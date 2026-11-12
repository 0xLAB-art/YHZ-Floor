from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import json

# Provisioned material
sig1_hex = "6c0b14d85ce691184385dc679debae235867751469f2636446dab6e954b1e6fd8ee71a60db9f985693db92c709b695ebc108a094c4a4be8b28fdcb0f921bee"
sig2_hex = "6c0b14d85ce691184385dc679debae235867751469f2636446dab6e954b1e6fda4d5cb158cf69d694d03669e6833b970930682a366b34e95b7d8843f53a5a1cf"
z1_hex = "de43e90e7225acf39e7df91ed636aca37c9a7c6069233a599167ee06db56ff4a"
z2_hex = "de0d9942e754db374b4c66fe177b8d7720e7f405cb46205f89883d15dd86026e"
challenge_msg_hex = "5776a4f51a0bd9cae0de8ab5fcfcb2289a77599b30ee57c3d1ea22f15a24f4b9"

# Parse signatures
r = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:], 16)
s2 = int(sig2_hex[64:], 16)

# Parse message digests
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# NIST P-256 curve order
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

# Recover nonce k
# s1 = k^-1 * (z1 + r*d) mod n
# s2 = k^-1 * (z2 + r*d) mod n
# s1 - s2 = k^-1 * (z1 - z2) mod n
# k = (z1 - z2) * inverse(s1 - s2, n) mod n
k = (z1 - z2) * pow(s1 - s2, -1, n) % n

# Recover private key d
# s1 = k^-1 * (z1 + r*d) mod n
# s1 * k = z1 + r*d mod n
# d = (s1 * k - z1) * inverse(r, n) mod n
d = (s1 * k - z1) * pow(r, -1, n) % n

print(f"Recovered d: {hex(d)}")
print(f"Recovered k: {hex(k)}")

# Verify by signing challenge message
d_hex = format(d, '064x')
key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
challenge_msg = bytes.fromhex(challenge_msg_hex)
signature = signer.sign(SHA256.new(challenge_msg))
sig_hex = signature.hex()

print(f"Signature: {sig_hex}")

# Verify the signature
verifier = DSS.new(key, 'fips-186-3')
try:
    verifier.verify(SHA256.new(challenge_msg), bytes.fromhex(sig_hex))
    print("Signature verified!")
except:
    print("Signature verification failed!")

# Output claim
claim = {"d_hex": d_hex, "sig_hex": sig_hex}
print(f"CLAIM:{json.dumps(claim)}")