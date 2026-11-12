import json
import sys

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def recover_private_key(r, s1, z1, s2, z2, n):
    """Recover private key from two signatures with the same r value."""
    # Calculate k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None
    
    k = (numerator * modinv(denominator, n)) % n
    
    # Calculate d = (s1 * k - z1) / r mod n
    numerator = (s1 * k - z1) % n
    d = (numerator * modinv(r, n)) % n
    
    return d

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Extract signatures
sig1 = instance['signatures'][0]
sig2 = instance['signatures'][1]

r = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
z1 = int(sig1['z'], 16)
s2 = int(sig2['s'], 16)
z2 = int(sig2['z'], 16)

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Recover private key
d = recover_private_key(r, s1, z1, s2, z2, n)

# If that doesn't work, try the negation
if d is None:
    d = recover_private_key(r, s1, z1, s2, z2, n)

# Format as 64 lowercase hex characters
d_hex = format(d, '064x')

# Output
print(json.dumps({"d": d_hex}))