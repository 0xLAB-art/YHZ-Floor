import json
import sys

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def recover_private_key(r, s1, s2, z1, z2, n):
    """Recover private key from two signatures with same r"""
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # d = (s1 * k - z1) / r mod n
    numerator = (s1 * k - z1) % n
    d = (numerator * modinv(r, n)) % n
    
    return d

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Extract signature data
r = int(instance['signatures'][0]['r'], 16)
s1 = int(instance['signatures'][0]['s'], 16)
z1 = int(instance['signatures'][0]['z'], 16)
s2 = int(instance['signatures'][1]['s'], 16)
z2 = int(instance['signatures'][1]['z'], 16)

# Recover private key
d = recover_private_key(r, s1, s2, z1, z2, n)

# Output result
print(json.dumps({"d": format(d, '064x')}))