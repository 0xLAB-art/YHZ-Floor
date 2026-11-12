import json
import sys
import base64
from hashlib import sha256

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
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

def int_to_hex64(n):
    """Convert integer to 64-character lowercase hex string"""
    return format(n % (2**256), '064x')

# SECP256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# Decode signatures
signatures = []
for sig in data['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append({'r': r, 's': s, 'z': z})

# Find duplicate r values
r_groups = {}
for idx, sig in enumerate(signatures):
    r = sig['r']
    if r not in r_groups:
        r_groups[r] = []
    r_groups[r].append(idx)

# Find a pair with same r
k = None
d = None
for r, indices in r_groups.items():
    if len(indices) >= 2:
        # Use first two signatures with same r
        idx1, idx2 = indices[0], indices[1]
        sig1 = signatures[idx1]
        sig2 = signatures[idx2]
        
        r = sig1['r']
        s1 = sig1['s']
        s2 = sig2['s']
        z1 = sig1['z']
        z2 = sig2['z']
        
        # Calculate k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        k = (numerator * modinv(denominator, n)) % n
        
        # Calculate d = (s*k - z) / r mod n
        numerator = (s1 * k - z1) % n
        d = (numerator * modinv(r, n)) % n
        
        break

# Output result
result = {
    "d": int_to_hex64(d),
    "k": int_to_hex64(k)
}
print(json.dumps(result))
