import json
import sys

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

def recover_private_key(sigs):
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with the same r value
    r_groups = {}
    for i, sig in enumerate(sigs):
        r = int(sig['r'], 16)
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append((i, sig))
    
    # Find a pair with same r
    for r, group in r_groups.items():
        if len(group) >= 2:
            sig1 = group[0][1]
            sig2 = group[1][1]
            
            r = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            z1 = int(sig1['z'], 16)
            s2 = int(sig2['s'], 16)
            z2 = int(sig2['z'], 16)
            
            # Calculate k from the two signatures
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Calculate private key d
            d = (((s1 * k - z1) % n) * modinv(r, n)) % n
            
            return d
    
    return None

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

d = recover_private_key(instance['signatures'])

# Output result
print(json.dumps({"d": format(d, '064x')}))