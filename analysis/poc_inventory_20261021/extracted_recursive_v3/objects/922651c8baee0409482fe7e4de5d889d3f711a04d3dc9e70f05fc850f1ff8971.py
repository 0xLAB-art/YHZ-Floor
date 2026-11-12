import sys
import json
import hashlib
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

# Provisioned material
sig1_hex = "299751d9d981307c2638cd950eb43798cc1f1c3039eb676554a2884e666bc5ace4beb5ef214549615d472f159f7a6a5201ad914e387bf7438909d4894a728173"
sig2_hex = "299751d9d981307c2638cd950eb43798cc1f1c3039eb676554a2884e666bc5ac8e6e20976aed333880c1984c2dec3ef515f7a020da9b0df8d2d8b22023f34e37"
z1_hex = "e4a2d5051405f27808fa6490f92c26f690f3ccd17c341cc34af6391daec1d987"
z2_hex = "ca9eb07f7a0164d64356d379a7423c2fcfd5c343efbb46d106b54d069dc55dce"
challenge_msg_hex = "c027cdfaa858475c8cbf0d405c59cf7f295571814c31bb47e8d4685602c84506"

# Parse signatures (64 bytes = r || s, each 32 bytes)
sig1 = bytes.fromhex(sig1_hex)
sig2 = bytes.fromhex(sig2_hex)
r1 = int.from_bytes(sig1[:32], 'big')
s1 = int.from_bytes(sig1[32:], 'big')
r2 = int.from_bytes(sig2[:32], 'big')
s2 = int.from_bytes(sig2[32:], 'big')

# Verify r values are the same (same nonce k)
assert r1 == r2, f"r values differ: {r1} vs {r2}"
r = r1

z1 = int.from_bytes(bytes.fromhex(z1_hex), 'big')
z2 = int.from_bytes(bytes.fromhex(z2_hex), 'big')

# NIST P-256 curve order
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# Recover k: k = (z1 - z2) * (s1 - s2)^(-1) mod n
k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n

# Recover d: d = (s1 * k - z1) * r^(-1) mod n
d = ((s1 * k - z1) * pow(r, -1, n)) % n

d_hex = format(d, '064x')
print(f"Recovered d: {d_hex}", file=sys.stderr)

# Create signature for challenge message
key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
challenge_hash = SHA256.new(bytes.fromhex(challenge_msg_hex))
sig = signer.sign(challenge_hash)
sig_hex = sig.hex()
print(f"Challenge signature: {sig_hex}", file=sys.stderr)

# Output claim
claim = {"d_hex": d_hex, "sig_hex": sig_hex}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()