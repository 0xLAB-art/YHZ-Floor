import json
import sys
import base64
from hashlib import sha256

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

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

# Load instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# SECP256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

# Parse signatures
signatures = []
for sig in data['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append({'r': r, 's': s, 'z': z})

# Find signatures with the same r value (nonce reuse)
r_groups = {}
for i, sig in enumerate(signatures):
    r = sig['r']
    if r not in r_groups:
        r_groups[r] = []
    r_groups[r].append(i)

# Find a pair with same r
d = None
k = None

for r, indices in r_groups.items():
    if len(indices) >= 2:
        i1, i2 = indices[0], indices[1]
        sig1 = signatures[i1]
        sig2 = signatures[i2]
        
        z1, s1 = sig1['z'], sig1['s']
        z2, s2 = sig2['z'], sig2['s']
        
        # Calculate k = (z1 - z2) / (s1 - s2) mod n
        z_diff = (z1 - z2) % n
        s_diff = (s1 - s2) % n
        
        if s_diff != 0:
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Calculate d = (s*k - z) / r mod n
            r_inv = modinv(r, n)
            d = ((s1 * k - z1) * r_inv) % n
            
            # Verify with second signature
            d_check = ((s2 * k - z2) * r_inv) % n
            if d == d_check:
                break

# Output result
result = {
    "d": int_to_hex(d),
    "k": int_to_hex(k)
}

print(json.dumps(result))