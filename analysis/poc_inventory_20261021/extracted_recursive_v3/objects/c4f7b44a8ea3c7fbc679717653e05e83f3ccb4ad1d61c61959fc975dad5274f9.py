import json
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

sig1_hex = "ac86767bebe074a579cdaada0a32f5e19395ae7a4d814ef656743bf438b3999b8e3a91553a945527ddd82571344c9f1285fde633287a003833f0cc684618e3bb"
sig2_hex = "ac86767bebe074a579cdaada0a32f5e19395ae7a4d814ef656743bf438b3999b895fdefafdfe08e469b72b97c7538756bfadd72e33e14d1d399f524b3b744769"
z1_hex = "866dfdc05d549aaafc24abfa9b4a864c3aca3662e46d4078cd9056b91035cfbe"
z2_hex = "88a5dce36eaddacdba38a5d4f3e4c504c6db6558d8ea775c2add19b92ad5dd0e"
challenge_msg_hex = "ea8a390b3dbb34c9f6ba2cd7b19767e2df57014971d451c8ecce9731e31f6ca8"

n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

r1 = int(sig1_hex[0:64], 16)
s1 = int(sig1_hex[64:128], 16)
r2 = int(sig2_hex[0:64], 16)
s2 = int(sig2_hex[64:128], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

assert r1 == r2

# k = (z1 - z2) / (s1 - s2)  mod n
k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n
# d = (s1 * k - z1) / r      mod n
d = ((s1 * k - z1) * pow(r1, -1, n)) % n

# sanity: recompute k from signature 2
k_check = ((z2 + r1 * d) * pow(s2, -1, n)) % n
assert k_check == k
assert 1 <= d < n

key = ECC.construct(curve='NIST P-256', d=d)
h = SHA256.new(bytes.fromhex(challenge_msg_hex))
sig = DSS.new(key, 'fips-186-3').sign(h)

# verify locally
DSS.new(key, 'fips-186-3').verify(SHA256.new(bytes.fromhex(challenge_msg_hex)), sig)

print(json.dumps({"d_hex": "%064x" % d, "sig_hex": sig.hex()}, separators=(',', ':')), flush=True)
print("CLAIM:" + json.dumps({"d_hex": "%064x" % d, "sig_hex": sig.hex()}, separators=(',', ':')), flush=True)