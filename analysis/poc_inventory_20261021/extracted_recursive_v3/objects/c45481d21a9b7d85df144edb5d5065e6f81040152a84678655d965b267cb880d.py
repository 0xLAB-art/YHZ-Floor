import json
import sys
import base64
from hashlib import sha256

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
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

# secp256k1 curve parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Decode public key
x = int.from_bytes(base64.b64decode(instance['public_key']['x']), 'big')
y = int.from_bytes(base64.b64decode(instance['public_key']['y']), 'big')

# Decode signatures
signatures = []
for sig in instance['signatures']:
    r = int.from_bytes(base64.b64decode(sig['r']), 'big')
    s = int.from_bytes(base64.b64decode(sig['s']), 'big')
    z = int.from_bytes(base64.b64decode(sig['z']), 'big')
    signatures.append((r, s, z))

# Look for repeated r values (nonce reuse)
r_map = {}
for i, (r, s, z) in enumerate(signatures):
    if r in r_map:
        # Found nonce reuse! Extract private key
        j = r_map[r]
        r1, s1, z1 = signatures[j]
        r2, s2, z2 = signatures[i]
        
        # k = (z1 - z2) / (s1 - s2) mod n
        # d = (s*k - z) / r mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        k = (z_diff * modinv(s_diff, n)) % n
        d = ((s1 * k - z1) * modinv(r1, n)) % n
        
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        k_hex = format(k, '064x')
        
        print(json.dumps({"d": d_hex, "k": k_hex}))
        sys.exit(0)
    
    r_map[r] = i

# Should not reach here if there's nonce reuse
print(json.dumps({"d": "0" * 64, "k": "0" * 64}))