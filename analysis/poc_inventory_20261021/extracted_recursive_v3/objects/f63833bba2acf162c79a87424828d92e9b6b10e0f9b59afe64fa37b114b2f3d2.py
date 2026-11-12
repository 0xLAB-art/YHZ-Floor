import sys
import json
import base64
import hashlib

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# SECP256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Parse signatures
sig1 = instance['signatures'][0]
sig2 = instance['signatures'][1]

r1 = bytes_to_int(base64.b64decode(sig1['r']))
s1 = bytes_to_int(base64.b64decode(sig1['s']))
z1 = bytes_to_int(base64.b64decode(sig1['z']))

r2 = bytes_to_int(base64.b64decode(sig2['r']))
s2 = bytes_to_int(base64.b64decode(sig2['s']))
z2 = bytes_to_int(base64.b64decode(sig2['z']))

# Verify both signatures use the same r
assert r1 == r2
r = r1

# Recover k from the nonce reuse
# k = (z1 - z2) / (s1 - s2) mod n
z_diff = (z1 - z2) % n
s_diff = (s1 - s2) % n
s_diff_inv = modinv(s_diff, n)
k = (z_diff * s_diff_inv) % n

# Recover private key d
# d = (s*k - z) / r mod n
r_inv = modinv(r, n)
d = ((s1 * k - z1) * r_inv) % n

# Format as 64 lowercase hex characters
d_hex = format(d, '064x')

# Output result
result = {"d": d_hex}
print(json.dumps(result))