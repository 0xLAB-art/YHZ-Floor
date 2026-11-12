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

def recover_private_key(r, s1, z1, s2, z2, n):
    """Recover private key from two signatures with same nonce"""
    # From s1 = k^(-1) * (z1 + r*d) mod n
    # From s2 = k^(-1) * (z2 + r*d) mod n
    # We get: s1 - s2 = k^(-1) * (z1 - z2) mod n
    # Therefore: k = (z1 - z2) / (s1 - s2) mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    k = (z_diff * modinv(s_diff, n)) % n
    
    # Now recover d from: s1 = k^(-1) * (z1 + r*d) mod n
    # s1 * k = z1 + r*d mod n
    # d = (s1*k - z1) / r mod n
    
    k_inv = modinv(k, n)
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return d, k

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 curve order
n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

signatures = instance['signatures']

# Find signatures with duplicate r values
r_map = {}
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    if r in r_map:
        # Found duplicate! Recover the key
        j = r_map[r]
        
        s1 = int(signatures[j]['s'], 16)
        z1 = int(signatures[j]['z'], 16)
        s2 = int(sig['s'], 16)
        z2 = int(sig['z'], 16)
        
        d, k = recover_private_key(r, s1, z1, s2, z2, n)
        
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        k_hex = format(k, '064x')
        
        result = {"d": d_hex, "k": k_hex}
        print(json.dumps(result))
        sys.exit(0)
    
    r_map[r] = i

# Should not reach here if there are duplicate r values
print(json.dumps({"d": "0" * 64, "k": "0" * 64}))