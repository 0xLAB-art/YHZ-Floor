import json
import sys
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

# Provisioned material
sig1_hex = "c4db2f6993ac5bede8bd578c988dd81d925f7c219d5893d90de195cec17f9cf25e0dd140c597ab66eda9c7438f795ad20d2339d828f216cb278fdbb48d36a498"
sig2_hex = "c4db2f6993ac5bede8bd578c988dd81d925f7c219d5893d90de195cec17f9cf22c801fd536737c17419df2510cf808123f12714c339bfc986a2891305fc0158b"
z1_hex = "c2c165571d6560e5f168be87b5cb00b03c06c3a6169f0eb19271461b57e24bf0"
z2_hex = "66db8f554ffaf86bcca0c0f5e4f8ac999a0868718b5e38b299f3ceb79b0bec1a"
challenge_msg_hex = "dc28379c1c71fdbf86adbc3bdcc90361037ca17e75f1284ec987819189246de6"

# Parse signatures: first 64 hex chars = r, last 64 = s
r_hex = sig1_hex[:64]
s1_hex = sig1_hex[64:]
s2_hex = sig2_hex[64:]

r = int(r_hex, 16)
s1 = int(s1_hex, 16)
s2 = int(s2_hex, 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# NIST P-256 curve order
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# Recover k: k = (z1 - z2) * (s1 - s2)^(-1) mod n
z_diff = (z1 - z2) % n
s_diff = (s1 - s2) % n
s_diff_inv = pow(s_diff, -1, n)
k = (z_diff * s_diff_inv) % n

# Recover d: d = (s1 * k - z1) * r^(-1) mod n
r_inv = pow(r, -1, n)
d = ((s1 * k - z1) % n * r_inv) % n

# Create signature for challenge message
key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
challenge_hash = SHA256.new(bytes.fromhex(challenge_msg_hex))
sig = signer.sign(challenge_hash)
sig_hex = sig.hex()

d_hex = format(d, '064x')

print(f"CLAIM:{{\"d_hex\": \"{d_hex}\", \"sig_hex\": \"{sig_hex}\"}}")
sys.stdout.flush()