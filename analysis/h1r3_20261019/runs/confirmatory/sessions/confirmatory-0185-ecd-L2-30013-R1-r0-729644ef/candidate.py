import json
import sys

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
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = instance['signatures']

# Find signatures with same r (nonce reuse)
r_map = {}
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with same r
pair_indices = None
for r, indices in r_map.items():
    if len(indices) >= 2:
        pair_indices = indices[:2]
        break

if pair_indices is None:
    raise Exception("No nonce reuse found")

# Get the two signatures with same r
i1, i2 = pair_indices
sig1 = signatures[i1]
sig2 = signatures[i2]

r = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
s2 = int(sig2['s'], 16)
z1 = int(sig1['z'], 16)
z2 = int(sig2['z'], 16)

# Recover k from the nonce reuse
# k = (z1 - z2) / (s1 - s2) mod n
numerator = (z1 - z2) % n
denominator = (s1 - s2) % n
k = (numerator * modinv(denominator, n)) % n

# Recover private key d
# d = (s*k - z) / r mod n
numerator = (s1 * k - z1) % n
d = (numerator * modinv(r, n)) % n

# Format as 64 lowercase hex characters
d_hex = format(d, '064x')

# Output
result = {"d": d_hex}
print(json.dumps(result))
