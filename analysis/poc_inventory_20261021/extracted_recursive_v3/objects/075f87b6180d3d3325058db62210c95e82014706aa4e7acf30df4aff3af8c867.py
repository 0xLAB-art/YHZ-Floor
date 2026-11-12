import json
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from Crypto.Util.number import inverse

sig1_hex = "7c136b57aac33ad2ca67810aa1c052a39c4c2c39a0cfe8da2fc7ea28d419decb8a8e47cddeff574a9b508b61431c41532f87d6c6348f5654ebad469d0b5b6259"
sig2_hex = "7c136b57aac33ad2ca67810aa1c052a39c4c2c39a0cfe8da2fc7ea28d419decb37d75e003be88bf284a2c211a82746aa3fc1b9a33ef652727df479c44cfd7c5b"
z1_hex = "3c01ab82de5471e7f11612c49d4f538d82a432c843ca75f38f4433da4e773c10"
z2_hex = "0dee3e18e96da07d8d95c1cf607977cd3d8bfffaa083a9117580152fb00b42a1"
challenge_msg_hex = "8fa2e0a5be74ad292bcbf765b27ed3993f99255dde648b4763e14159f5a50cf4"

curve = ECC._curves["NIST P-256"]
n = int(curve.order)

r1 = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:], 16)
r2 = int(sig2_hex[:64], 16)
s2 = int(sig2_hex[64:], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

assert r1 == r2, "r values differ -> nonce is NOT reused"
r = r1

k = (z1 - z2) * inverse((s1 - s2) % n, n) % n
d = ((s1 * k - z1) * inverse(r, n)) % n
assert 1 <= d < n

key = ECC.construct(curve="NIST P-256", d=d)

# self-check: recovered key verifies both provisioned signatures over their z
for sh, zh in ((sig1_hex, z1_hex), (sig2_hex, z2_hex)):
    DSS.new(key, "fips-186-3").verify(SHA256.new(bytes.fromhex(zh)), bytes.fromhex(sh))

sig = DSS.new(key, "fips-186-3").sign(SHA256.new(bytes.fromhex(challenge_msg_hex)))
assert DSS.new(key, "fips-186-3").verify(SHA256.new(bytes.fromhex(challenge_msg_hex)), sig)

claim = {"d_hex": "%064x" % d, "sig_hex": sig.hex()}
print("CLAIM:" + json.dumps(claim, separators=(",", ":")))