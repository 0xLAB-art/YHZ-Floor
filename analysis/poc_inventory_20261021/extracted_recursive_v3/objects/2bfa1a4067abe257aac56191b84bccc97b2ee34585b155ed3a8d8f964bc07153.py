import json
import sys

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

signatures = data['signatures']

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Find duplicate r values
r_to_indices = {}
for i, sig in enumerate(signatures):
    r = sig['r']
    if r not in r_to_indices:
        r_to_indices[r] = []
    r_to_indices[r].append(i)

# Find pairs with same r
duplicate_r = None
indices = None
for r, idxs in r_to_indices.items():
    if len(idxs) >= 2:
        duplicate_r = r
        indices = idxs[:2]
        break

if duplicate_r:
    i1, i2 = indices
    sig1 = signatures[i1]
    sig2 = signatures[i2]
    
    r = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    s2 = int(sig2['s'], 16)
    z1 = int(sig1['z'], 16)
    z2 = int(sig2['z'], 16)
    
    # Compute k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # Compute d = (s*k - z) / r mod n
    numerator = (s1 * k - z1) % n
    d = (numerator * modinv(r, n)) % n
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    print(json.dumps({"d": d_hex, "k": k_hex}))