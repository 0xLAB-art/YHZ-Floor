import json
import sys
import base64


def mod_inverse(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
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

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# Decode public key
x = int.from_bytes(base64.b64decode(data['public_key']['x']), 'big')
y = int.from_bytes(base64.b64decode(data['public_key']['y']), 'big')

# Decode signatures
signatures = []
for sig in data['signatures']:
    r = int.from_bytes(base64.b64decode(sig['r']), 'big')
    s = int.from_bytes(base64.b64decode(sig['s']), 'big')
    z = int.from_bytes(base64.b64decode(sig['z']), 'big')
    signatures.append((r, s, z))

# Look for repeated r values (nonce reuse attack)
r_map = {}
for i, (r, s, z) in enumerate(signatures):
    if r in r_map:
        r_map[r].append((i, s, z))
    else:
        r_map[r] = [(i, s, z)]

# Find pairs with same r
for r, pairs in r_map.items():
    if len(pairs) >= 2:
        # Use first two signatures with same r
        i1, s1, z1 = pairs[0]
        i2, s2, z2 = pairs[1]
        
        # k = (z1 - z2) / (s1 - s2) mod n
        # d = (s1*k - z1) / r mod n
        
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        
        if denominator != 0:
            k = (numerator * mod_inverse(denominator, n)) % n
            
            # Recover private key
            d_numerator = (s1 * k - z1) % n
            d = (d_numerator * mod_inverse(r, n)) % n
            
            # Output the private key
            d_hex = format(d, '064x')
            print(json.dumps({"d": d_hex}))
            sys.exit(0)

# Fallback (shouldn't reach here if nonce reuse exists)
print(json.dumps({"d": "0" * 64}))
