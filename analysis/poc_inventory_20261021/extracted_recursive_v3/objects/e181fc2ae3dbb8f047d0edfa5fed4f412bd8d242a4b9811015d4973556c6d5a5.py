from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
r = int("b7b12f089ad4ce6bb4e1941dbbed8ac7a643521f0707161937579fa4b2e57da0", 16)
s1 = int("976b5d2a33dce87865fdf5ace8b1138d9d29af11c7b8ef320ccfa254bb326ddf", 16)
s2 = int("d9f7d13aa9911c29849bd4a0f84ab36b3923bf75b45db5e94acad98d978463a9", 16)
z1 = int("703b2142de626412e98392939d77907037306714dd317cada70ab02b0e20ee9b", 16)
z2 = int("07e825430e3f683dd385fb44183ce49744cca47071a1d0dba97e73faf30c3cce", 16)

k = (pow(s1 - s2, -1, n) * (z1 - z2)) % n
d = (pow(r, -1, n) * (s1 * k - z1)) % n

print("k", hex(k))
print("d", hex(d))

key = ECC.construct(curve="NIST P-256", d=d)
h = SHA256.new(bytes.fromhex("7b47be04fe71d06ecb367183e5a2ff0c182a8ff9c98efb94a35498832a625e71"))
sig = DSS.new(key, "fips-186-3").sign(h)
sig_hex = sig.hex()
print(sig_hex, len(sig_hex))

h2 = SHA256.new(bytes.fromhex("7b47be04fe71d06ecb367183e5a2ff0c182a8ff9c98efb94a35498832a625e71"))
DSS.new(key, "fips-186-3").verify(h2, sig)
print("verified")

import json
print("CLAIM:" + json.dumps({"d_hex": "%064x" % d, "sig_hex": sig_hex}))