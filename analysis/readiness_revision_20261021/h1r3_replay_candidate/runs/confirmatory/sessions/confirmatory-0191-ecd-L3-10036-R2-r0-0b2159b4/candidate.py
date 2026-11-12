import sys
import json
import base64
import hashlib

def mod_inverse(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return (x % m + m) % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n % (2**256), '064x')

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Decode signatures
signatures = []
for sig in instance['signatures']:
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
    if r in r_map:
        # Found duplicate! Use these two signatures
        idx1 = r_map[r]
        idx2 = i
        
        s1 = signatures[idx1]['s']
        s2 = signatures[idx2]['s']
        z1 = signatures[idx1]['z']
        z2 = signatures[idx2]['z']
        r_val = r
        
        # Recover k: k = (z1 - z2) / (s1 - s2) mod n
        k = ((z1 - z2) % n) * mod_inverse((s1 - s2) % n, n) % n
        
        # Recover d: d = (s*k - z) / r mod n
        d = ((s1 * k - z1) % n) * mod_inverse(r_val, n) % n
        
        # Output result
        result = {
            'd': int_to_hex(d),
            'k': int_to_hex(k)
        }
        print(json.dumps(result))
        break
    else:
        r_map[r] = i
