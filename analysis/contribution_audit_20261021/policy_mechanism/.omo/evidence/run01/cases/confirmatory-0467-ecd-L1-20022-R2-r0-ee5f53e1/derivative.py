import sys
import json
import base64


def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def bytes_to_int(b):
    """Convert bytes to integer"""
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    """Convert integer to 64-character hex string"""
    hex_str = hex(n)[2:]
    return hex_str.zfill(64)

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Parse signatures
sig1 = instance['signatures'][0]
sig2 = instance['signatures'][1]

r1 = bytes_to_int(base64.b64decode(sig1['r']))
s1 = bytes_to_int(base64.b64decode(sig1['s']))
z1 = bytes_to_int(base64.b64decode(sig1['z']))

r2 = bytes_to_int(base64.b64decode(sig2['r']))
s2 = bytes_to_int(base64.b64decode(sig2['s']))
z2 = bytes_to_int(base64.b64decode(sig2['z']))

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Verify r values are the same
assert r1 == r2
r = r1

# Recover nonce k
# k = (z1 - z2) / (s1 - s2) mod n
numerator = (z1 - z2) % n
denominator = (s1 - s2) % n
k = (numerator * modinv(denominator, n)) % n

# Recover private key d
# d = (s * k - z) / r mod n
numerator = (s1 * k - z1) % n
d = (numerator * modinv(r, n)) % n

# Output result
result = {"d": int_to_hex(d)}
print(json.dumps(result))
