import sys
import json
import base64


def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
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
    """Convert bytes to integer"""
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    """Convert integer to 64-character lowercase hex string"""
    return format(n, '064x')

# SECP256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# Parse signatures
signatures = []
for sig in data['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append((r, s, z))

# Find signatures with same r value (nonce reuse)
r_dict = {}
for i, (r, s, z) in enumerate(signatures):
    if r not in r_dict:
        r_dict[r] = []
    r_dict[r].append((i, s, z))

# Find a pair with reused nonce
k_found = None
d_found = None

for r, pairs in r_dict.items():
    if len(pairs) >= 2:
        # Use first two signatures with same r
        i1, s1, z1 = pairs[0]
        i2, s2, z2 = pairs[1]
        
        # Recover k: k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        
        if denominator != 0:
            k = (numerator * modinv(denominator, n)) % n
            
            # Recover d: d = (s*k - z) / r mod n
            numerator_d = (s1 * k - z1) % n
            d = (numerator_d * modinv(r, n)) % n
            
            k_found = k
            d_found = d
            break

# Output result
result = {
    "d": int_to_hex(d_found),
    "k": int_to_hex(k_found)
}

print(json.dumps(result))
