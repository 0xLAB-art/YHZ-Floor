import json
import sys

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm"""
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = egcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = egcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

signatures = data['signatures']

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Find signatures with the same r value (nonce reuse)
r_map = {}
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with the same r
d = None
for r_val, indices in r_map.items():
    if len(indices) >= 2:
        i1, i2 = indices[0], indices[1]
        
        r = int(signatures[i1]['r'], 16)
        s1 = int(signatures[i1]['s'], 16)
        z1 = int(signatures[i1]['z'], 16)
        s2 = int(signatures[i2]['s'], 16)
        z2 = int(signatures[i2]['z'], 16)
        
        # Recover k from the two signatures
        # k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        k = (numerator * modinv(denominator, n)) % n
        
        # Recover d from k
        # d = (s*k - z) / r mod n
        d = ((s1 * k - z1) * modinv(r, n)) % n
        break

# Format as 64 lowercase hex characters
d_hex = format(d, '064x')

print(json.dumps({"d": d_hex}))
