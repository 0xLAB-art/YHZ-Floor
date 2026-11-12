import sys
import json

def modinv(a, m):
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

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

signatures = data['signatures']

# secp256k1 parameters
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Convert signatures to integers
sigs = []
for sig in signatures:
    sigs.append({
        'r': int(sig['r'], 16),
        's': int(sig['s'], 16),
        'z': int(sig['z'], 16)
    })

# Find signatures with same r
r_to_indices = {}
for i, sig in enumerate(sigs):
    r = sig['r']
    if r not in r_to_indices:
        r_to_indices[r] = []
    r_to_indices[r].append(i)

# Find a pair with same r
pair_indices = None
for r, indices in r_to_indices.items():
    if len(indices) >= 2:
        pair_indices = indices[:2]
        break

if pair_indices is None:
    raise ValueError("No repeated r found")

i1, i2 = pair_indices
sig1 = sigs[i1]
sig2 = sigs[i2]

r = sig1['r']
s1 = sig1['s']
s2 = sig2['s']
z1 = sig1['z']
z2 = sig2['z']

# Calculate k from: k = (z1 - z2) / (s1 - s2) mod n
numerator = (z1 - z2) % n
denominator = (s1 - s2) % n
k = (numerator * modinv(denominator, n)) % n

# Calculate d from: d = (s*k - z) / r mod n
d = ((s1 * k - z1) % n * modinv(r, n)) % n

# Format as 64 lowercase hex characters
d_hex = format(d, '064x')

print(json.dumps({"d": d_hex}))
