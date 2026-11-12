import json, time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

sig1_hex = "53d5b83238becfaddba690447de22d8f50f6156ea5f6a2ff070a5d17c8fbf34e850d75066d14db5de2040f54b3b2fc8463a594d74e9b3dfe05ec951a2706848d"
sig2_hex = "53d5b83238becfaddba690447de22d8f50f6156ea5f6a2ff070a5d17c8fbf34e828440a9fef7202ea5c71efb55d18dc95582fc1ce48c981b21a57c0ca00ce9ba"
z1_hex = "eed2ec6b4dc94516ed85f61e04e368a185cc1b8cacbf8912819e6fa1b3caa14b"
z2_hex = "64abacd59fd68dd120b481907e4b31ea1c6cb1c518b9318f23729d6bdc699031"
challenge_msg_hex = "1493b832129bc80152bff3d55aa9ca96d07cd584fbf953a25fd952296150a12c"

sig1 = bytes.fromhex(sig1_hex)
sig2 = bytes.fromhex(sig2_hex)
r1 = int.from_bytes(sig1[:32], "big")
s1 = int.from_bytes(sig1[32:], "big")
r2 = int.from_bytes(sig2[:32], "big")
s2 = int.from_bytes(sig2[32:], "big")
z1 = int.from_bytes(bytes.fromhex(z1_hex), "big")
z2 = int.from_bytes(bytes.fromhex(z2_hex), "big")

assert r1 == r2, "r mismatch"
r = r1

t0 = time.monotonic_ns()

ds = (s1 - s2) % n
dz = (z1 - z2) % n
k = (dz * pow(ds, -1, n)) % n
d = ((s1 * k - z1) * pow(r, -1, n)) % n

# self-consistency checks
chk1 = (pow(k, -1, n) * (z1 + r * d)) % n
chk2 = (pow(k, -1, n) * (z2 + r * d)) % n
ok = (chk1 == s1) and (chk2 == s2) and (1 <= d < n)

key = ECC.construct(curve="NIST P-256", d=d)
sig3 = DSS.new(key, "fips-186-3").sign(SHA256.new(bytes.fromhex(challenge_msg_hex)))

# verify locally
DSS.new(key, "fips-186-3").verify(SHA256.new(bytes.fromhex(challenge_msg_hex)), sig3)

elapsed = time.monotonic_ns() - t0

claim = {"d_hex": "%064x" % d, "sig_hex": sig3.hex()}
print("consistency_ok=%s r=%064x k=%064x" % (ok, r, k))
print("OPSPAN_NS:%d" % elapsed)
print("CLAIM:" + json.dumps(claim, separators=(",", ":")))