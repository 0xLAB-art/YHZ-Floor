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
    data = json.load(f)

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Parse signatures
sig1 = data['signatures'][0]
sig2 = data['signatures'][1]

r = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
z1 = int(sig1['z'], 16)

s2 = int(sig2['s'], 16)
z2 = int(sig2['z'], 16)

# Verify same r value
assert r == int(sig2['r'], 16), "r values must be the same"

# Recover nonce k from two signatures with same r
# k = (z1 - z2) / (s1 - s2) mod n
z_diff = (z1 - z2) % n
s_diff = (s1 - s2) % n
s_diff_inv = modinv(s_diff, n)
k = (z_diff * s_diff_inv) % n

# Recover private key d
# d = (s1 * k - z1) / r mod n
r_inv = modinv(r, n)
d = ((s1 * k - z1) * r_inv) % n

# Output as 64 hex characters (zero-padded)
result = {"d": format(d, '064x')}
print(json.dumps(result))