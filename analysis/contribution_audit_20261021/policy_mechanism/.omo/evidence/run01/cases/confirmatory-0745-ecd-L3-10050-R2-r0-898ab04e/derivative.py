import base64
import json
import sys


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

# secp256k1 curve parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# Decode signatures
signatures = []
for sig in data['signatures']:
    r = int.from_bytes(base64.b64decode(sig['r']), 'big')
    s = int.from_bytes(base64.b64decode(sig['s']), 'big')
    z = int.from_bytes(base64.b64decode(sig['z']), 'big')
    signatures.append({'r': r, 's': s, 'z': z})

# Find duplicate r values
r_map = {}
for i, sig in enumerate(signatures):
    r = sig['r']
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with the same r
k_found = None
d_found = None

for r, indices in r_map.items():
    if len(indices) >= 2:
        # Use first two signatures with same r
        i1, i2 = indices[0], indices[1]
        sig1 = signatures[i1]
        sig2 = signatures[i2]
        
        r = sig1['r']
        s1 = sig1['s']
        s2 = sig2['s']
        z1 = sig1['z']
        z2 = sig2['z']
        
        # Calculate k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        k = (numerator * modinv(denominator, n)) % n
        
        # Calculate d = (s * k - z) / r mod n
        numerator = (s1 * k - z1) % n
        d = (numerator * modinv(r, n)) % n
        
        k_found = k
        d_found = d
        break

# Format output as 64 lowercase hex characters
d_hex = format(d_found, '064x')
k_hex = format(k_found, '064x')

result = {
    "d": d_hex,
    "k": k_hex
}

print(json.dumps(result))
