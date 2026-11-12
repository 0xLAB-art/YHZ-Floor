import sys
import json
import base64
import hashlib

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

def mod_inverse(a, m):
    # Extended Euclidean Algorithm
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

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Decode public key
pub_x = base64.b64decode(instance['public_key']['x'])
pub_y = base64.b64decode(instance['public_key']['y'])

# Decode signatures
signatures = []
for sig in instance['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append({'r': r, 's': s, 'z': z})

# ECDSA parameters for secp256k1 (standard Bitcoin curve)
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Find duplicate r values (nonce reuse)
r_map = {}
for i, sig in enumerate(signatures):
    r = sig['r']
    if r in r_map:
        # Found nonce reuse!
        j = r_map[r]
        sig1 = signatures[j]
        sig2 = sig
        
        # Recover k and d
        r = sig1['r']
        s1 = sig1['s']
        s2 = sig2['s']
        z1 = sig1['z']
        z2 = sig2['z']
        
        # k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        k = (numerator * mod_inverse(denominator, n)) % n
        
        # d = (s*k - z) / r mod n
        numerator = (s1 * k - z1) % n
        d = (numerator * mod_inverse(r, n)) % n
        
        # Output result
        result = {
            'd': int_to_hex(d),
            'k': int_to_hex(k)
        }
        print(json.dumps(result))
        break
    else:
        r_map[r] = i
