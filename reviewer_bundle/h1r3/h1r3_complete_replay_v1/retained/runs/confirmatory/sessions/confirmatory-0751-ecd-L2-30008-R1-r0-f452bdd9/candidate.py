import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = instance['signatures']

# Convert hex to integers
sigs = []
for sig in signatures:
    sigs.append({
        'r': int(sig['r'], 16),
        's': int(sig['s'], 16),
        'z': int(sig['z'], 16)
    })

# Find signatures with same r value
r_map = {}
for i, sig in enumerate(sigs):
    r = sig['r']
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with same r
d = None
for r, indices in r_map.items():
    if len(indices) >= 2:
        # Use first two signatures with same r
        i, j = indices[0], indices[1]
        
        r1 = sigs[i]['r']
        s1 = sigs[i]['s']
        z1 = sigs[i]['z']
        
        r2 = sigs[j]['r']
        s2 = sigs[j]['s']
        z2 = sigs[j]['z']
        
        # Recover k: k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        k = (numerator * modinv(denominator, n)) % n
        
        # Recover d: d = (s * k - z) / r mod n
        numerator = (s1 * k - z1) % n
        denominator = r1
        d = (numerator * modinv(denominator, n)) % n
        
        break

# Format output
result = {"d": format(d, '064x')}
print(json.dumps(result))
