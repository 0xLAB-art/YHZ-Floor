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

def recover_key_from_repeated_nonce(r, s1, z1, s2, z2, n):
    """Recover private key when same nonce is used for two signatures."""
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # d = (s*k - z) / r mod n
    numerator = (s1 * k - z1) % n
    d = (numerator * modinv(r, n)) % n
    
    return d, k

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# SECP256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = instance['signatures']

# Find signatures with repeated r values
r_map = {}
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    if r in r_map:
        # Found repeated r - exploit it
        j = r_map[r]
        s1 = int(signatures[j]['s'], 16)
        z1 = int(signatures[j]['z'], 16)
        s2 = int(sig['s'], 16)
        z2 = int(sig['z'], 16)
        
        d, k = recover_key_from_repeated_nonce(r, s1, z1, s2, z2, n)
        
        # Output result
        result = {
            "d": format(d, '064x'),
            "k": format(k, '064x')
        }
        print(json.dumps(result))
        sys.exit(0)
    else:
        r_map[r] = i