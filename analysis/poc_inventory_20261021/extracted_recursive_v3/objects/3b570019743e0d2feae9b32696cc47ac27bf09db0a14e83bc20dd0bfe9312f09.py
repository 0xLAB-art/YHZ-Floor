import json
import sys

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(r, s1, s2, z1, z2, n):
    """Recover private key from two signatures with same nonce"""
    # k = (z1 - z2) / (s1 - s2) mod n
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    
    k = (z_diff * modinv(s_diff, n)) % n
    
    # d = (s * k - z) / r mod n
    d = ((s1 * k - z1) % n * modinv(r, n)) % n
    
    return d, k

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 parameters
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = instance['signatures']

# Find signatures with duplicate r values
r_map = {}
for idx, sig in enumerate(signatures):
    r_val = sig['r']
    if r_val not in r_map:
        r_map[r_val] = []
    r_map[r_val].append(idx)

# Find a pair with duplicate r
duplicate_r = None
indices = None
for r_val, idx_list in r_map.items():
    if len(idx_list) >= 2:
        duplicate_r = r_val
        indices = idx_list[:2]
        break

if duplicate_r is None:
    raise Exception("No duplicate r values found")

# Extract signature data
idx1, idx2 = indices
sig1 = signatures[idx1]
sig2 = signatures[idx2]

r = int(duplicate_r, 16)
s1 = int(sig1['s'], 16)
s2 = int(sig2['s'], 16)
z1 = int(sig1['z'], 16)
z2 = int(sig2['z'], 16)

# Recover private key
d, k = recover_private_key(r, s1, s2, z1, z2, n)

# Format output
result = {
    "d": format(d, '064x'),
    "k": format(k, '064x')
}

print(json.dumps(result))