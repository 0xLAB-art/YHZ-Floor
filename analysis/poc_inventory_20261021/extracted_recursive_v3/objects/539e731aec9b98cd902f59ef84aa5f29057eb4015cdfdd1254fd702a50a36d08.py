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

# Extract signatures
sig1 = instance['signatures'][0]
sig2 = instance['signatures'][1]

r = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
z1 = int(sig1['z'], 16)
s2 = int(sig2['s'], 16)
z2 = int(sig2['z'], 16)

# Verify same r value
assert r == int(sig2['r'], 16), "r values must match for nonce reuse attack"

# Recover private key using nonce reuse
# d = (s1*z2 - s2*z1) * (r*(s1 - s2))^(-1) mod n
numerator = (s1 * z2 - s2 * z1) % n
denominator = (r * (s1 - s2)) % n
d = (numerator * modinv(denominator, n)) % n

# Format as 64 hex characters
d_hex = format(d, '064x')

# Output
print(json.dumps({"d": d_hex}))
