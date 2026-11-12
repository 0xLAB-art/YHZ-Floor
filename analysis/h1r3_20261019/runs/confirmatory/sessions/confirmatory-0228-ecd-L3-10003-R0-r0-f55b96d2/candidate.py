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
    instance = json.load(f)

# secp256k1 parameters
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = instance['signatures']

# Find duplicate r values
r_dict = {}
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    if r not in r_dict:
        r_dict[r] = []
    r_dict[r].append(i)

# Find a pair with the same r
duplicate_r = None
for r, indices in r_dict.items():
    if len(indices) >= 2:
        duplicate_r = r
        idx1, idx2 = indices[0], indices[1]
        break

if duplicate_r is None:
    raise ValueError("No duplicate r found")

# Get the two signatures with the same r
sig1 = signatures[idx1]
sig2 = signatures[idx2]

r = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
z1 = int(sig1['z'], 16)
s2 = int(sig2['s'], 16)
z2 = int(sig2['z'], 16)

# Recover k: k = (z1 - z2) / (s1 - s2) mod n
z_diff = (z1 - z2) % n
s_diff = (s1 - s2) % n
s_diff_inv = modinv(s_diff, n)
k = (z_diff * s_diff_inv) % n

# Recover d: d = (s*k - z) / r mod n
r_inv = modinv(r, n)
d = ((s1 * k - z1) * r_inv) % n

# Format output
k_hex = format(k, '064x')
d_hex = format(d, '064x')

print(json.dumps({"d": d_hex, "k": k_hex}))
