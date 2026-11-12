import sys
import json
import hashlib

def modinv(a, m):
    """Modular multiplicative inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
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

signatures = data['signatures']

# Convert hex to integers
sigs = []
for sig in signatures:
    sigs.append({
        'r': int(sig['r'], 16),
        's': int(sig['s'], 16),
        'z': int(sig['z'], 16)
    })

# Find duplicate r values
r_map = {}
for i, sig in enumerate(sigs):
    r = sig['r']
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with the same r
d = None
k = None

for r_val, indices in r_map.items():
    if len(indices) >= 2:
        # Use first two signatures with same r
        i1, i2 = indices[0], indices[1]
        
        r = sigs[i1]['r']
        s1 = sigs[i1]['s']
        s2 = sigs[i2]['s']
        z1 = sigs[i1]['z']
        z2 = sigs[i2]['z']
        
        # k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        
        if denominator != 0:
            k = (numerator * modinv(denominator, n)) % n
            
            # d = (s * k - z) / r mod n
            d = ((s1 * k - z1) % n * modinv(r, n)) % n
            
            # Verify with second signature
            d_check = ((s2 * k - z2) % n * modinv(r, n)) % n
            
            if d == d_check:
                break

# Format output
result = {
    "d": format(d, '064x'),
    "k": format(k, '064x')
}

print(json.dumps(result))
