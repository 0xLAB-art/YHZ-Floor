import sys
import json

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

def recover_key_from_nonce_reuse(r, s1, z1, s2, z2, n):
    """Recover private key from two signatures with same nonce"""
    # Calculate k = (z1 - z2) / (s1 - s2) mod n
    k = ((z1 - z2) % n * modinv((s1 - s2) % n, n)) % n
    
    # Calculate d = (s * k - z) / r mod n
    d = ((s1 * k - z1) % n * modinv(r, n)) % n
    
    return d, k

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 parameters
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Parse signatures
sigs = []
for sig in instance['signatures']:
    sigs.append({
        'r': int(sig['r'], 16),
        's': int(sig['s'], 16),
        'z': int(sig['z'], 16)
    })

# Find signatures with duplicate r values
r_map = {}
for i, sig in enumerate(sigs):
    r = sig['r']
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with duplicate r
for r, indices in r_map.items():
    if len(indices) >= 2:
        i1, i2 = indices[0], indices[1]
        sig1, sig2 = sigs[i1], sigs[i2]
        
        d, k = recover_key_from_nonce_reuse(
            r, 
            sig1['s'], sig1['z'],
            sig2['s'], sig2['z'],
            n
        )
        
        # Format output
        d_hex = format(d, '064x')
        k_hex = format(k, '064x')
        
        print(json.dumps({"d": d_hex, "k": k_hex}))
        break
