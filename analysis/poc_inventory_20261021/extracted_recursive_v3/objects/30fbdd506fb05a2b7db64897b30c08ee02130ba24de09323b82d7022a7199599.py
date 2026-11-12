import json
import sys

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
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
    data = json.load(f)

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = data['signatures']

# Find duplicate r values
r_map = {}
for i, sig in enumerate(signatures):
    r = sig['r']
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with the same r
duplicate_r = None
indices = None
for r, idx_list in r_map.items():
    if len(idx_list) >= 2:
        duplicate_r = r
        indices = idx_list[:2]
        break

if duplicate_r is None:
    raise Exception("No duplicate r found")

# Get the two signatures with the same r
i1, i2 = indices
sig1 = signatures[i1]
sig2 = signatures[i2]

r = int(duplicate_r, 16)
s1 = int(sig1['s'], 16)
s2 = int(sig2['s'], 16)
z1 = int(sig1['z'], 16)
z2 = int(sig2['z'], 16)

# Recover k: k = (z1 - z2) / (s1 - s2) mod n
z_diff = (z1 - z2) % n
s_diff = (s1 - s2) % n
s_diff_inv = modinv(s_diff, n)
k = (z_diff * s_diff_inv) % n

# Recover d: d = (s*k - z) / r mod n
r_inv = modinv(r, n)
d = ((s1 * k - z1) * r_inv) % n

# Format as 64 character hex strings
k_hex = format(k, '064x')
d_hex = format(d, '064x')

print(json.dumps({"d": d_hex, "k": k_hex}))