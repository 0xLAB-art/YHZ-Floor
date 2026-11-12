import sys
import json
from collections import defaultdict

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n):
    """Recover private key k (nonce) and d when same nonce is used twice"""
    # k = (z1 - z2) / (s1 - s2) mod n
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    if s_diff_inv is None:
        return None, None
    
    k = (z_diff * s_diff_inv) % n
    
    # d = (s * k - z) / r mod n
    r_inv = modinv(r, n)
    if r_inv is None:
        return None, None
    
    d = ((s1 * k - z1) * r_inv) % n
    
    return k, d

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = instance['signatures']

# Group signatures by r value to find nonce reuse
r_groups = defaultdict(list)
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    s = int(sig['s'], 16)
    z = int(sig['z'], 16)
    r_groups[r].append((i, s, z))

# Find a pair with same r value
k_found = None
d_found = None

for r, sigs in r_groups.items():
    if len(sigs) >= 2:
        # We have nonce reuse
        i1, s1, z1 = sigs[0]
        i2, s2, z2 = sigs[1]
        
        k, d = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
        
        if k is not None and d is not None:
            k_found = k
            d_found = d
            break

# Format output
if k_found is not None and d_found is not None:
    d_hex = format(d_found, '064x')
    k_hex = format(k_found, '064x')
else:
    d_hex = '0' * 64
    k_hex = '0' * 64

print(json.dumps({"d": d_hex, "k": k_hex}))
