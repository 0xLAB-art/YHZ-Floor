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
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Parse signatures
signatures = []
for sig in data['signatures']:
    r = int(sig['r'], 16)
    s = int(sig['s'], 16)
    z = int(sig['z'], 16)
    signatures.append((r, s, z))

# Find signatures with same r (indices 4 and 5, 0-indexed)
sig1 = signatures[4]  # r, s1, z1
sig2 = signatures[5]  # r, s2, z2

r = sig1[0]
s1 = sig1[1]
z1 = sig1[2]
s2 = sig2[1]
z2 = sig2[2]

# Recover k from the two signatures with same r
# k = (z1 - z2) * (s1 - s2)^(-1) mod n
z_diff = (z1 - z2) % n
s_diff = (s1 - s2) % n
s_diff_inv = modinv(s_diff, n)
k = (z_diff * s_diff_inv) % n

# Recover private key d
# d = r^(-1) * (s * k - z) mod n
r_inv = modinv(r, n)
d = (r_inv * ((s1 * k - z1) % n)) % n

# Format as 64 lowercase hex characters
d_hex = format(d, '064x')

print(json.dumps({"d": d_hex}))
