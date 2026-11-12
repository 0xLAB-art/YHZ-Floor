from Crypto.Hash import SHA256
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC

# Provisioned material
sig1_hex = "77b47ea9d4b0e96b96e53471392bae3360700ad617778bfb4121587c58362909718c3dc05c6ff771fdb716b3778e9a97968cc49f6d6e63929330175dbcde89e6"
sig2_hex = "77b47ea9d4b0e96b96e53471392bae3360700ad617778bfb4121587c5836290938105d6541841213db0a3b6be54f04a60f7a7d28a62d0791b6c1b70fa4f17c59"
z1_hex = "b0241047664982ffe9d660e096b09f74f6816a08d9fa43fc60a2277789af214f"
z2_hex = "016881f7884543eef82c75d558e7e96ba1a1de3e253aeb7a93a52008ce38eb29"
challenge_msg_hex = "5e067701d91007196147df9ae7787a4ad921a286be1cb4407473ef4a7d4ce3"

# Parse signatures
r = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:], 16)
s2 = int(sig2_hex[64:], 16)

z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# NIST P-256 order
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

# Recover nonce k from: s1 - s2 = k^(-1) * (z1 - z2) mod n
k = (z1 - z2) * pow(s1 - s2, -1, n) % n

# Recover private key d from: s1 = k^(-1) * (z1 + r*d) mod n
d = (s1 * k - z1) * pow(r, -1, n) % n

print(f"Recovered d: {format(d, '064x')}")

# Verify by constructing key and signing challenge
key = ECC.construct(curve='NIST P-256', d=d)
 signer = DSS.new(key, 'fips-186-3')
msg = bytes.fromhex(challenge_msg_hex)
sig = signer.sign(SHA256.new(msg))
sig_hex = sig.hex()
print(f"Signature: {sig_hex}")

# Verify the signature
verifier = DSS.new(key, 'fips-186-3')
try:
    verifier.verify(SHA256.new(msg), bytes.fromhex(sig_hex))
    print("Signature verified!")
except:
    print("Signature verification failed!")

print(f"CLAIM: {{\"d_hex\": \"{format(d, '064x')}\", \"sig_hex\": \"{sig_hex}\"}}")