import sys
import json
import base64
import hashlib

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def bytes_to_int(b):
    """Convert bytes to integer."""
    return int.from_bytes(b, byteorder='big')

def int_to_hex(n):
    """Convert integer to 64 lowercase hex characters."""
    return format(n, '064x')

# NIST P-256 curve parameters
p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Decode public key
pub_x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
pub_y = bytes_to_int(base64.b64decode(instance['public_key']['y']))

# Decode signatures
sig1 = instance['signatures'][0]
r1 = bytes_to_int(base64.b64decode(sig1['r']))
s1 = bytes_to_int(base64.b64decode(sig1['s']))
z1 = bytes_to_int(base64.b64decode(sig1['z']))

sig2 = instance['signatures'][1]
r2 = bytes_to_int(base64.b64decode(sig2['r']))
s2 = bytes_to_int(base64.b64decode(sig2['s']))
z2 = bytes_to_int(base64.b64decode(sig2['z']))

# Both signatures share the same r value (nonce reuse attack)
# ECDSA equations:
# s1 = k^-1 * (z1 + r * d) mod n
# s2 = k^-1 * (z2 + r * d) mod n
#
# From these we can derive:
# k = (z1 - z2) / (s1 - s2) mod n
# d = (s * k - z) / r mod n

# Calculate k (the nonce)
s_diff = (s1 - s2) % n
z_diff = (z1 - z2) % n
s_diff_inv = modinv(s_diff, n)
k = (z_diff * s_diff_inv) % n

# Calculate d (the private key)
r_inv = modinv(r1, n)
d = (r_inv * (s1 * k - z1)) % n

# Output result
result = {"d": int_to_hex(d)}
print(json.dumps(result))
