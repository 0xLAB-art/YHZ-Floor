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

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = instance['signatures']

# Find signatures with same r value
r_groups = {}
for i, sig in enumerate(signatures):
    r = sig['r']
    if r not in r_groups:
        r_groups[r] = []
    r_groups[r].append(i)

# Find a pair with same r
for r_hex, indices in r_groups.items():
    if len(indices) >= 2:
        i, j = indices[0], indices[1]
        
        r = int(r_hex, 16)
        s1 = int(signatures[i]['s'], 16)
        s2 = int(signatures[j]['s'], 16)
        z1 = int(signatures[i]['z'], 16)
        z2 = int(signatures[j]['z'], 16)
        
        # Calculate k from the two signatures
        k = ((z1 - z2) * modinv(s1 - s2, n)) % n
        
        # Calculate private key d
        d = ((s1 * k - z1) * modinv(r, n)) % n
        
        # Output result
        result = {"d": format(d, '064x')}
        print(json.dumps(result))
        break
