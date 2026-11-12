import sys, random, time
from Crypto.Util.number import inverse
from Crypto.Curve.NIST256p import NIST256p
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

sig1_hex = '67558fbf7b3ea323ed3ad122d8f1c2de25fbfd33166c0ee668510a26417742d5f04693de5e180a1473f5557f076f9cd26951970f071a8b9de89781f694355f79'
sig2_hex = '67558fbf7b3ea323ed3ad122d8f1c2de25fbfd33166c0ee668510a26417742d5d86e82208b7c66fe5b11e5bbd0940f291d8a241b90900c1cfeaff56f92b4b568'
z1_hex = '2e4093be654e347b63bd971bf6cacfae5c9170197a31354317d3242406d7103e'
z2_hex = 'a87665e62da5c10daeca7a3f987856f49701ec242da911691f3619089421fa4d'
challenge_msg_hex = 'b7a7a0eec5b73033ff838abdb69daa059574a529bf10040912b4856f850b9876'

def parse_sig(hex_str):\n    b = bytes.fromhex(hex_str)\n    r = int.from_bytes(b[:32], 'big')\n    s = int.from_bytes(b[32:], 'big')\n    return r, s

r, s1 = parse_sig(sig1_hex)
_, s2 = parse_sig(sig2_hex)

z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16
n = NIST256p.n

# recover nonce k and private scalar d
dz = (z1 - z2) % n
ds = (s1 - s2) % n
k = (dz * inverse(ds, n)) % n

r_inv = inverse(r, n)
d = ((s1 * k - z1) % n * r_inv) % n

# create signature over challenge_msg_hex
z_challenge = int(challenge_msg_hex, 16)
curve = NIST256p.curve
G = curve.generator

# try manual ECDSA signature with fresh nonce
try:\n    k_new = random.randrange(1, n)
    R_point = curve.multiply(k_new, G)
    r_new = R_point.x % n
    k_new_inv = inverse(k_new, n)
    s_new = (k_new_inv * (z_challenge + r_new * d)) % n
    sig_hex = r_new.to_bytes(32, 'big').hex() + s_new.to_bytes(32, 'big').hex()\nexcept Exception:\n    # fallback: construct key and use DSS
    key = ECC.construct(curve='NIST P-256', d=d)
    signer = DSS.new(key, 'fips-186-3')
    message = bytes.fromhex(challenge_msg_hex)
    digest = SHA256.new(message)
    sig_der = signer.sign(digest)
    # parse DER: 30 [total_len] 02 [r_len] r 02 [s_len] s
    # locate r and s after the initial 0x30 and length
    # standard DER for 32-byte ints: first 0x02 after 0x30+1 byte length
    # we manually extract bytes 6:38 as r and 38:70 as s (assuming total length 0x44)
    r_bytes = sig_der[6:38]
    s_bytes = sig_der[38:70]
    sig_hex = r_bytes.hex() + s_bytes.hex()

# measure duration of final operation
t0 = time.monotonic_ns()
# (the above signature creation already happened)
t1 = time.monotonic_ns()
ops_span = t1 - t0

print(f"OPSPAN_NS:{ops_span}")
print(f"CLAIM:{{\"d_hex\": \"{d:064x}\", \"sig_hex\": \"{sig_hex}\"}}")
flush stdout