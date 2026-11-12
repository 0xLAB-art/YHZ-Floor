import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def recover_key_from_duplicate_nonce(r, s1, z1, s2, z2, n):
    """Recover private key d and nonce k from two signatures with same r"""
    # k = (z1 - z2) / (s1 - s2) mod n
    k = ((z1 - z2) * modinv(s1 - s2, n)) % n
    
    # d = (s * k - z) / r mod n
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return d, k

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 parameters
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = instance['signatures']

# Find duplicate r values
r_map = {}
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    if r in r_map:
        # Found duplicate!
        j = r_map[r]
        s1 = int(signatures[j]['s'], 16)
        z1 = int(signatures[j]['z'], 16)
        s2 = int(sig['s'], 16)
        z2 = int(sig['z'], 16)
        
        d, k = recover_key_from_duplicate_nonce(r, s1, z1, s2, z2, n)
        
        # Output result
        result = {
            "d": format(d, '064x'),
            "k": format(k, '064x')
        }
        print(json.dumps(result))
        sys.exit(0)
    else:
        r_map[r] = i