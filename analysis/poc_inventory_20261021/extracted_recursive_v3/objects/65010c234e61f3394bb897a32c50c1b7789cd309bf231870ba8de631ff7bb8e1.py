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

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 parameters
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

# Calculate k from the two signatures
# k = (z1 - z2) / (s1 - s2) mod n
k = ((z1 - z2) * modinv((s1 - s2) % n, n)) % n

# Calculate private key d
# d = (s1 * k - z1) / r mod n
d = ((s1 * k - z1) * modinv(r, n)) % n

# Output result
result = {"d": format(d, '064x')}
print(json.dumps(result))