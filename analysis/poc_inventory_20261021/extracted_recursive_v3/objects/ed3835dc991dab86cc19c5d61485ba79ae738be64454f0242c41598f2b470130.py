import json
import sys
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

def modinv(a, n):
    return pow(a, -1, n)

# NIST P-256 order
N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

# Parse signatures (r || s, 32 bytes each)
sig1 = bytes.fromhex('26bc55d3e39c7bc204272b0d5b4c1ec781c07a3e866fc8771cf80a36cb74bec8d7ea89e280ea918f99e97783e6a6bf62929f70d216260d934f0623a7893459d9')
sig2 = bytes.fromhex('26bc55d3e39c7bc204272b0d5b4c1ec781c07a3e866fc8771cf80a36cb74bec8058443dd647478f8bbd81e28add7eec020875d52c42d40fcac702f3c4853cbcb')

r = int.from_bytes(sig1[:32], 'big')
s1 = int.from_bytes(sig1[32:], 'big')
s2 = int.from_bytes(sig2[32:], 'big')

z1 = int.from_bytes(bytes.fromhex('c2a6a07aa8b69e278c87ff09bd18b030f1ac67905bc9cd8c20b51e2c22e049a8'), 'big')
z2 = int.from_bytes(bytes.fromhex('196e4784561b11bcfd61c2f51f96bbc8ed928b3b35308813823c6225229c3123'), 'big')

# Recover k: k = (z1 - z2) * (s1 - s2)^(-1) mod n
k = ((z1 - z2) * modinv((s1 - s2) % N, N)) % N

# Recover d: d = (s1 * k - z1) * r^(-1) mod n
d = ((s1 * k - z1) * modinv(r, N)) % N

d_hex = format(d, '064x')

# Create signature for challenge message
challenge_msg = bytes.fromhex('2a23dba7ea310cb6a1035aba38807147ebc51f432365d73589f1598ec9b45cfa')
key = ECC.construct(curve='NIST P-256', d=d)
signer = DSS.new(key, 'fips-186-3')
sig = signer.sign(SHA256.new(challenge_msg))
sig_hex = sig.hex()

claim = {'d_hex': d_hex, 'sig_hex': sig_hex}
print(f'CLAIM:{json.dumps(claim)}')
sys.stdout.flush()