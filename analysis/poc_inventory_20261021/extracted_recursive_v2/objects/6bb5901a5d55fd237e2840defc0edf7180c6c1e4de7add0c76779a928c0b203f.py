import sys
import json

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm."""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

sig1 = data['signatures'][0]
sig2 = data['signatures'][1]

r = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
z1 = int(sig1['z'], 16)
s2 = int(sig2['s'], 16)
z2 = int(sig2['z'], 16)

# Compute private key from nonce reuse
# d = (s1*z2 - s2*z1) / (s1*r - s2*r) mod n
numerator = (s1 * z2 - s2 * z1) % n
denominator = (s1 * r - s2 * r) % n
d = (numerator * modinv(denominator, n)) % n

# Output result
result = {"d": format(d, '064x')}
print(json.dumps(result))
