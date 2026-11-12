import json
import sys

from typing import Tuple

def modinv(a: int, m: int) -> int:
    """Compute modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def bytes_to_int(b: bytes) -> int:
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n: int) -> str:
    """Convert integer to 64-character hex string."""
    hex_str = hex(n)[2:].rstrip('L')
    return hex_str.zfill(64)

# ECDSA parameters for secp256k1
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Parse signatures
import base64

sig1 = instance['signatures'][0]
sig2 = instance['signatures'][1]

r1 = bytes_to_int(base64.b64decode(sig1['r']))
s1 = bytes_to_int(base64.b64decode(sig1['s']))
z1 = bytes_to_int(base64.b64decode(sig1['z']))

r2 = bytes_to_int(base64.b64decode(sig2['r']))
s2 = bytes_to_int(base64.b64decode(sig2['s']))
z2 = bytes_to_int(base64.b64decode(sig2['z']))

# Both signatures share the same r value (nonce reuse attack)
# ECDSA signature equations:
# s1 = k^-1 * (z1 + r * d) mod n
# s2 = k^-1 * (z2 + r * d) mod n
#
# From these we can derive:
# s1 - s2 = k^-1 * (z1 - z2) mod n
# k = (z1 - z2) / (s1 - s2) mod n
# d = (s * k - z) / r mod n

# Calculate k (the nonce)
z_diff = (z1 - z2) % n
s_diff = (s1 - s2) % n
s_diff_inv = modinv(s_diff, n)
k = (z_diff * s_diff_inv) % n

# Calculate d (the private key)
r_inv = modinv(r1, n)
d = (r_inv * (s1 * k - z1)) % n

# Output result
result = {"d": int_to_hex(d)}
print(json.dumps(result))
