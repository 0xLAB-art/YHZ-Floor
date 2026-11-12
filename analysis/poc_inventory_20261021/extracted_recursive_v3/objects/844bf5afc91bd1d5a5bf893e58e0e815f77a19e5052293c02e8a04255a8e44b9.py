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
    """Extended Euclidean algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# SECP256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Extract signatures
sig1 = instance['signatures'][0]
sig2 = instance['signatures'][1]

r1 = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
z1 = int(sig1['z'], 16)

r2 = int(sig2['r'], 16)
s2 = int(sig2['s'], 16)
z2 = int(sig2['z'], 16)

# Verify that r values are the same (nonce reuse)
assert r1 == r2, "r values must be the same for nonce reuse attack"

r = r1

# Recover the nonce k
# k = (z1 - z2) / (s1 - s2) mod n
numerator = (z1 - z2) % n
denominator = (s1 - s2) % n
k = (numerator * modinv(denominator, n)) % n

# Recover the private key d
# d = (s * k - z) / r mod n
numerator_d = (s1 * k - z1) % n
d = (numerator_d * modinv(r, n)) % n

# Output the result
result = {
    "d": format(d, '064x')
}

print(json.dumps(result))