import json
import sys
import base64
import hashlib

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def mod_inverse(a, m):
    # Extended Euclidean Algorithm
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
    # Calculate k from two signatures with same r
    k = ((z1 - z2) * mod_inverse((s1 - s2) % n, n)) % n
    
    # Calculate private key d
    d = ((s1 * k - z1) * mod_inverse(r, n)) % n
    
    return d, k

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# SECP256k1 parameters
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Decode signatures
signatures = []
for sig in instance['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append({'r': r, 's': s, 'z': z})

# Find duplicate r values
r_to_sigs = {}
for i, sig in enumerate(signatures):
    r = sig['r']
    if r not in r_to_sigs:
        r_to_sigs[r] = []
    r_to_sigs[r].append(i)

# Find pairs with same r
for r, indices in r_to_sigs.items():
    if len(indices) >= 2:
        # Use first two signatures with same r
        idx1, idx2 = indices[0], indices[1]
        sig1 = signatures[idx1]
        sig2 = signatures[idx2]
        
        # Recover private key
        d, k = recover_private_key(
            sig1['r'],
            sig1['s'], sig1['z'],
            sig2['s'], sig2['z'],
            n
        )
        
        # Format output
        d_hex = format(d, '064x')
        k_hex = format(k, '064x')
        
        print(json.dumps({"d": d_hex, "k": k_hex}))
        break