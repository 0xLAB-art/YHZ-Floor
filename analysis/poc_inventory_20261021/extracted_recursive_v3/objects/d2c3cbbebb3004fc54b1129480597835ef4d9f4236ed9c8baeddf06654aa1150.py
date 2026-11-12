import hashlib
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import time

# Provisioned material
sig1_hex = '46a6a7a028bfe9b9bd80464a3d206e9337cf4f96c249597f43bc7003af05382d0f5e1a223ad5f1c5fd7aa9f9e749b7bb591a2d437d86ea34de34bb48f9a34972'
sig2_hex = '46a6a7a028bfe9b9bd80464a3d206e9337cf4f96c249597f43bc7003af05382dc3e5460bf5a4a3d58d01fd69dad7264e312fe9455aa49f3ec07cb4abcf9c76f3'
z1_hex = '448e41fdc56a17442db0073e2e44d7be7b9fa72ee7e130639efd7fa64e9e671f'
z2_hex = '48c88c5591ca28b3932e0371e91ebb4a3c182aa2eec76bb3447439d7a7d8ffad'
challenge_msg_hex = 'f90d26e3b112e9403f7a2828547b44051bd767ff06fe8a76ad9b7ad91b2732e6'

# Curve order for NIST P-256
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

def h2i(h):
    return int(h, 16)

r1 = h2i(sig1_hex[:64])
s1 = h2i(sig1_hex[64:])
r2 = h2i(sig2_hex[:64])
s2 = h2i(sig2_hex[64:])
assert r1 == r2, 'Nonce reuse not detected: r values differ'
r = r1
z1 = h2i(z1_hex)
z2 = h2i(z2_hex)

s1_minus_s2 = (s1 - s2) % n
z1_minus_z2 = (z1 - z2) % n
inv_s_diff = pow(s1_minus_s2, -1, n)
k = (z1_minus_z2 * inv_s_diff) % n

r_inv = pow(r, -1, n)
d = ((s1 * k - z1) % n) * r_inv % n
assert 1 <= d < n

start = time.monotonic_ns()

priv_key = ECC.construct(curve='NIST P-256', d=d)
msg_bytes = bytes.fromhex(challenge_msg_hex)
hash_obj = SHA256.new(msg_bytes)
signer = DSS.new(priv_key, 'fips-186-3')
signature_der = signer.sign(hash_obj)  # DER encoded SEQUENCE of two INTEGERs

# Parse DER to get r and s as integers
def parse_der_signature(der):
    if len(der) < 2 or der[0] != 0x30:
        raise ValueError('Invalid DER signature: not a SEQUENCE')
    length = der[1]
    if length + 2 > len(der):
        raise ValueError('Invalid length')
    pos = 2
    # first INTEGER
    if der[pos] != 0x02:
        raise ValueError('Expected INTEGER')
    pos += 1
    len_r = der[pos]
    pos += 1
    r_bytes = der[pos:pos+len_r]
    pos += len_r
    # second INTEGER
    if der[pos] != 0x02:
        raise ValueError('Expected INTEGER for s')
    pos += 1
    len_s = der[pos]
    pos += 1
    s_bytes = der[pos:pos+len_s]
    r_int = int.from_bytes(r_bytes, 'big')
    s_int = int.from_bytes(s_bytes, 'big')
    return r_int, s_int

r_sig, s_sig = parse_der_signature(signature_der)
# enforce low-s
if s_sig > n // 2:
    s_sig = n - s_sig
r_bytes = r_sig.to_bytes(32, 'big')
s_bytes = s_sig.to_bytes(32, 'big')
sig_hex = r_bytes.hex() + s_bytes.hex()

end = time.monotonic_ns()
opspan = end - start

d_hex = format(d, '064x')
claim = {'d_hex': d_hex, 'sig_hex': sig_hex}
print(f'OPSPAN_NS:{opspan}')
print(f'CLAIM:{claim}')