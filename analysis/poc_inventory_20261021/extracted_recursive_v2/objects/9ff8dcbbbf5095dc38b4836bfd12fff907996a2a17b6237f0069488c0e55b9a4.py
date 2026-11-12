import sys
import json
import base64
import hashlib

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

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

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Find duplicate r values
r_map = {}
for i, sig in enumerate(signatures):
    r = sig['r']
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with same r
for r, indices in r_map.items():
    if len(indices) >= 2:
        i1, i2 = indices[0], indices[1]
        sig1 = signatures[i1]
        sig2 = signatures[i2]
        
        r = sig1['r']
        s1 = sig1['s']
        s2 = sig2['s']
        z1 = sig1['z']
        z2 = sig2['z']
        
        # k = (z1 - z2) / (s1 - s2) mod n
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        k = (z_diff * modinv(s_diff, n)) % n
        
        # d = (s*k - z) / r mod n
        d = ((s1 * k - z1) * modinv(r, n)) % n
        
        # Output
        result = {
            'd': int_to_hex(d),
            'k': int_to_hex(k)
        }
        print(json.dumps(result))
        break
