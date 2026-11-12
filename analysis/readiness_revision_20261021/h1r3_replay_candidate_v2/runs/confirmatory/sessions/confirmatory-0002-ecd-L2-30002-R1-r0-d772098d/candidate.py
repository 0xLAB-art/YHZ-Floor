import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

signatures = data['signatures']

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Convert signatures to integers
sigs = []
for sig in signatures:
    r = int(sig['r'], 16)
    s = int(sig['s'], 16)
    z = int(sig['z'], 16)
    sigs.append((r, s, z))

# Find signatures with the same r
r_map = {}
for i, (r, s, z) in enumerate(sigs):
    if r not in r_map:
        r_map[r] = []
    r_map[r].append((i, s, z))

# Find a pair with same r
d = None
for r, pairs in r_map.items():
    if len(pairs) >= 2:
        # Use first two signatures with same r
        i1, s1, z1 = pairs[0]
        i2, s2, z2 = pairs[1]
        
        # Compute k = (z1 - z2) / (s1 - s2) mod n
        z_diff = (z1 - z2) % n
        s_diff = (s1 - s2) % n
        
        if s_diff == 0:
            continue
            
        s_diff_inv = modinv(s_diff, n)
        k = (z_diff * s_diff_inv) % n
        
        # Compute d = (s1 * k - z1) / r mod n
        r_inv = modinv(r, n)
        d = ((s1 * k - z1) * r_inv) % n
        
        break

if d is None:
    # If no repeated r found, this shouldn't happen based on the instance
    d = 0

# Format output
d_hex = format(d, '064x')
result = {"d": d_hex}
print(json.dumps(result))
