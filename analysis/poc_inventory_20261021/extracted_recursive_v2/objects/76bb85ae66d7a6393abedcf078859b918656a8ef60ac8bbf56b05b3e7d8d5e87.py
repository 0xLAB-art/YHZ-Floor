import sys
import json

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

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = data['signatures']

# Convert signatures to integers
sigs = []
for sig in signatures:
    r = int(sig['r'], 16)
    s = int(sig['s'], 16)
    z = int(sig['z'], 16)
    sigs.append((r, s, z))

# Find signatures with same r value (nonce reuse)
r_map = {}
for i, (r, s, z) in enumerate(sigs):
    if r not in r_map:
        r_map[r] = []
    r_map[r].append((i, s, z))

# Find pair with reused nonce
d = None
for r, pairs in r_map.items():
    if len(pairs) >= 2:
        # Use first two signatures with same r
        i1, s1, z1 = pairs[0]
        i2, s2, z2 = pairs[1]
        
        # Calculate k from the two signatures
        # k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        k = (numerator * modinv(denominator, n)) % n
        
        # Calculate d from k
        # s1 = k^(-1) * (z1 + r*d) mod n
        # s1 * k = z1 + r*d mod n
        # d = (s1*k - z1) / r mod n
        d = ((s1 * k - z1) * modinv(r, n)) % n
        break

# Format as 64 lowercase hex characters
d_hex = format(d, '064x')

print(json.dumps({"d": d_hex}))
