import hashlib
import time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

# provisioned data
sig1_hex = "18badceb62b870ea57c2a51de05e253db391949af734cefd81c56a972ae4a51d4dc0313ef83af30a5e2a93b227177dcf41234da16df35c7dce1f5adea3ab178a"
sig2_hex = "18badceb62b870ea57c2a51de05e253db391949af734cefd81c56a972ae4a51dae69d58d5583f49c0e9168cc54d45fccafff7f8f7f8ebfb9dabcc2dc0db0a36182b5"
z1_hex = "ba8510a7bcf7a0ba002f0c823ba0b4d66ebafab949665de240099633c0e4482e"
z2_hex = "620f92081bc5e11214fd110cb5242410b4dfa654837a73e5a05ebdb9cc44dea8"
challenge_msg_hex = "7e59dbd198d1830d5d08f73d774b49a97c7c1b1da9485134daf102d7b32b4953"

# curve order for NIST P-256
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# split signatures
r = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:], 16)
s2 = int(sig2_hex[64:], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# compute d
num = (s1 * z2 - s2 * z1) % n
den = (r * ((s2 - s1) % n)) % n
den_inv = pow(den, -1, n)
d = (num * den_inv) % n

# recover private key
start = time.monotonic_ns()
key = ECC.construct(curve='p256', d=d)
h = SHA256.new(bytes.fromhex(challenge_msg_hex))
signer = DSS.new(key, 'fips-186-3')
signature = signer.sign(h)
sig_hex = signature.hex()
end = time.monotonic_ns()

# output
print(f"OPSPAN_NS:{end - start}", flush=True)
print(f"CLAIM:{{\"d_hex\": \"{d:064x}\", \"sig_hex\": \"{sig_hex}\"}}", flush=True)