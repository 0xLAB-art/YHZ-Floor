from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

# Provisioned material
sig1_hex = "cb04fc95c6a56cfcdc403e5cf8b4fc85da56bb796062347965357f5fa53b370a6875ab416f1148c286d86848eb620b1791203cc527c04884122bcde172f42760"
sig2_hex = "cb04fc95c6a56cfcdc403e5cf8b4fc85da56bb796062347965357f5fa53b370af90ee31a2900f71d2bda42ce164981c82d7c80a5229e21afc57c820b3c6ad8f9"
# Fixed: z1_hex was 63 chars, pad with leading zero
z1_hex = "0b559bd561f8c7e826d272a927fb5588d9290e0cadbe3c85c90ab5e0a3810974"
z2_hex = "80b1bb39af73b86963a154a4310cc8ad068f0712b4f0fd85b61778fea3bd916e"
# Fixed: challenge_msg_hex was 63 chars, pad with leading zero
challenge_msg_hex = "0cba33d4148fac68707e35a533bdcdb308de9e72a0823ebaac8d5525974645ad"

# Parse signatures
r1 = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:], 16)
r2 = int(sig2_hex[:64], 16)
s2 = int(sig2_hex[64:], 16)

z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# NIST P-256 curve order
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

# Recover k: k = (z1 - z2) * (s1 - s2)^(-1) mod n
k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n

# Recover d: d = (s1*k - z1) * r^(-1) mod n
d = ((s1 * k - z1) * pow(r1, -1, n)) % n

print(f"Recovered d: {format(d, '064x')}")

# Sign challenge message
key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
challenge_msg = bytes.fromhex(challenge_msg_hex)
sig = signer.sign(SHA256.new(challenge_msg))
sig_hex = sig.hex()
print(f"Signature: {sig_hex}")

# Verify
verifier = DSS.new(key, 'fips-186-3')
try:
    verifier.verify(SHA256.new(challenge_msg), bytes.fromhex(sig_hex))
    print("Signature verified!")
except Exception as e:
    print(f"Signature verification failed: {e}")

print(f"CLAIM: {{\"d_hex\": \"{format(d, '064x')}\", \"sig_hex\": \"{sig_hex}\"}}")