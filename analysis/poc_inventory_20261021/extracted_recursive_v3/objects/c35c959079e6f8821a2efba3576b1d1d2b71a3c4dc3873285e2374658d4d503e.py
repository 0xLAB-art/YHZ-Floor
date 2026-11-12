import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
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

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# secp256k1 parameters
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = data['signatures']

# Find duplicate r values
r_to_indices = {}
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    if r not in r_to_indices:
        r_to_indices[r] = []
    r_to_indices[r].append(i)

# Find a pair with the same r
duplicate_r = None
indices = None
for r, idx_list in r_to_indices.items():
    if len(idx_list) >= 2:
        duplicate_r = r
        indices = idx_list[:2]
        break

if duplicate_r is None:
    raise ValueError("No duplicate r found")

# Get the two signatures with the same r
sig1 = signatures[indices[0]]
sig2 = signatures[indices[1]]

r = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
z1 = int(sig1['z'], 16)
s2 = int(sig2['s'], 16)
z2 = int(sig2['z'], 16)

# Recover k: k = (z1 - z2) / (s1 - s2) mod n
k = ((z1 - z2) * modinv(s1 - s2, n)) % n

# Recover d: d = (s * k - z) / r mod n
d = ((s1 * k - z1) * modinv(r, n)) % n

# Format output
result = {
    "d": format(d, '064x'),
    "k": format(k, '064x')
}

print(json.dumps(result))