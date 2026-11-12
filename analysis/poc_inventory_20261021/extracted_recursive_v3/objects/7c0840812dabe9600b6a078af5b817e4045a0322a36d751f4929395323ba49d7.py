import json
import sys

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

# SECP256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Extract signature data
sig1 = instance['signatures'][0]
sig2 = instance['signatures'][1]

r = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
z1 = int(sig1['z'], 16)
s2 = int(sig2['s'], 16)
z2 = int(sig2['z'], 16)

# Same r value means same k was used
# s1 - s2 = k^(-1) * (z1 - z2) mod n
# k = (z1 - z2) / (s1 - s2) mod n

s_diff = (s1 - s2) % n
z_diff = (z1 - z2) % n

# k = z_diff * (s_diff)^(-1) mod n
k = (z_diff * modinv(s_diff, n)) % n

# Now recover d from: s1 = k^(-1) * (z1 + r*d) mod n
# k * s1 = z1 + r*d mod n
# d = (k*s1 - z1) / r mod n

k_inv = modinv(k, n)
d = ((s1 * k - z1) % n * modinv(r, n)) % n

# Format as 64 lowercase hex characters
d_hex = format(d, '064x')

# Output
result = {"d": d_hex}
print(json.dumps(result))