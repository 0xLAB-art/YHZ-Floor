import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def recover_private_key(sig1, sig2, n):
    """Recover private key from two signatures with same nonce"""
    r1 = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    
    r2 = int(sig2['r'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Verify same r value
    assert r1 == r2, "Signatures must share the same r value"
    r = r1
    
    # Calculate k = (z1 - z2) / (s1 - s2) mod n
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d = (s*k - z) / r mod n
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = instance['signatures']

# Find signatures with same r value (indices 4 and 5, 0-indexed)
sig5 = signatures[4]
sig6 = signatures[5]

# Recover private key
d = recover_private_key(sig5, sig6, n)

# Format as 64 lowercase hex characters
d_hex = format(d, '064x')

# Output result
print(json.dumps({"d": d_hex}))
