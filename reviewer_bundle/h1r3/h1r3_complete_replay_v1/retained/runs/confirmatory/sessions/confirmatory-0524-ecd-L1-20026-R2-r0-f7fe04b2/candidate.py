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
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def bytes_to_int(b):
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    """Convert integer to 64-character lowercase hex string."""
    hex_str = hex(n)[2:]
    return hex_str.zfill(64)

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Decode public key
x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
y = bytes_to_int(base64.b64decode(instance['public_key']['y']))

# Decode signatures
sigs = []
for sig in instance['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    sigs.append({'r': r, 's': s, 'z': z})

# ECDSA parameter for secp256k1
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Attack: same r value with different messages
# Given two signatures (r, s1, z1) and (r, s2, z2) with same r:
# s1 = k^-1 * (z1 + r*d) mod n
# s2 = k^-1 * (z2 + r*d) mod n
# 
# s1 - s2 = k^-1 * (z1 - z2) mod n
# k = (z1 - z2) / (s1 - s2) mod n
# 
# Then: d = (s*k - z) / r mod n

r = sigs[0]['r']
s1 = sigs[0]['s']
z1 = sigs[0]['z']
s2 = sigs[1]['s']
z2 = sigs[1]['z']

# Calculate k
z_diff = (z1 - z2) % n
s_diff = (s1 - s2) % n
s_diff_inv = modinv(s_diff, n)
k = (z_diff * s_diff_inv) % n

# Calculate private key d
r_inv = modinv(r, n)
d = ((s1 * k - z1) * r_inv) % n

# Output result
result = {"d": int_to_hex(d)}
print(json.dumps(result))
