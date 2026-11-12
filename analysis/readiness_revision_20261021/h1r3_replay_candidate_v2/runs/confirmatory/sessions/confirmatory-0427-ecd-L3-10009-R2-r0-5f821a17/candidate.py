import sys
import json
import base64
import hashlib

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm"""
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

def int_to_hex64(n):
    """Convert integer to 64-character lowercase hex string"""
    return format(n, '064x')

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

signatures = data['signatures']

# Decode signatures
sigs = []
for sig in signatures:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    sigs.append((r, s, z))

# Find duplicate r values (nonce reuse)
r_map = {}
for i, (r, s, z) in enumerate(sigs):
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with the same r
for r, indices in r_map.items():
    if len(indices) >= 2:
        i1, i2 = indices[0], indices[1]
        r1, s1, z1 = sigs[i1]
        r2, s2, z2 = sigs[i2]
        
        # Recover k and d
        # k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        k = (numerator * modinv(denominator, n)) % n
        
        # d = (s*k - z) / r mod n
        numerator = (s1 * k - z1) % n
        d = (numerator * modinv(r1, n)) % n
        
        # Output result
        result = {
            "d": int_to_hex64(d),
            "k": int_to_hex64(k)
        }
        print(json.dumps(result))
        break
