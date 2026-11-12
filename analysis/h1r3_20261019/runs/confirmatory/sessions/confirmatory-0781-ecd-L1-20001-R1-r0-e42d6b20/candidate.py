import sys
import json

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
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

def recover_private_key(r, s1, z1, s2, z2, n):
    """Recover private key from two signatures with same nonce"""
    # Calculate k = (z1 - z2) * (s1 - s2)^-1 mod n
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d = (s * k - z) * r^-1 mod n (using first signature)
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Parse signatures
sig1 = instance['signatures'][0]
sig2 = instance['signatures'][1]

r = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
z1 = int(sig1['z'], 16)
s2 = int(sig2['s'], 16)
z2 = int(sig2['z'], 16)

# Recover private key
d = recover_private_key(r, s1, z1, s2, z2, n)

# Format as 64 lowercase hex characters
d_hex = format(d, '064x')

# Output
print(json.dumps({"d": d_hex}))
