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

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

sig1 = instance['signatures'][0]
sig2 = instance['signatures'][1]

r1 = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
z1 = int(sig1['z'], 16)

r2 = int(sig2['r'], 16)
s2 = int(sig2['s'], 16)
z2 = int(sig2['z'], 16)

# Since r1 == r2, we have a nonce reuse attack
# From ECDSA: s = k^-1 * (z + r*d) mod n
# s1 = k^-1 * (z1 + r*d) mod n
# s2 = k^-1 * (z2 + r*d) mod n
# 
# s1 - s2 = k^-1 * (z1 - z2) mod n
# k = (z1 - z2) / (s1 - s2) mod n

s_diff = (s1 - s2) % n
z_diff = (z1 - z2) % n

# k = z_diff * modinv(s_diff, n) mod n
k = (z_diff * modinv(s_diff, n)) % n

# Now recover d from: s1 = k^-1 * (z1 + r*d) mod n
# s1 * k = z1 + r*d mod n
# d = (s1 * k - z1) / r mod n

d = ((s1 * k - z1) * modinv(r1, n)) % n

# Output
result = {"d": format(d, '064x')}
print(json.dumps(result))