import sys
import json

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = instance['signatures']

# Find signatures with the same r value (nonce reuse)
r_map = {}
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find pair with reused nonce
reused_r = None
indices = None
for r, idxs in r_map.items():
    if len(idxs) >= 2:
        reused_r = r
        indices = idxs[:2]
        break

if reused_r is None:
    raise Exception("No nonce reuse found")

# Get the two signatures with same r
sig1 = signatures[indices[0]]
sig2 = signatures[indices[1]]

r = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
s2 = int(sig2['s'], 16)
z1 = int(sig1['z'], 16)
z2 = int(sig2['z'], 16)

# Recover k from nonce reuse
# k = (z1 - z2) / (s1 - s2) mod n
z_diff = (z1 - z2) % n
s_diff = (s1 - s2) % n
s_diff_inv = modinv(s_diff, n)
k = (z_diff * s_diff_inv) % n

# Recover private key d
# d = (s*k - z) / r mod n
r_inv = modinv(r, n)
d = ((s1 * k - z1) * r_inv) % n

# Output as 64 lowercase hex characters
d_hex = format(d, '064x')
print(json.dumps({"d": d_hex}))