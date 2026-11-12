import json
import sys

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

signatures = instance['signatures']

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Convert hex strings to integers
sigs = []
for sig in signatures:
    sigs.append({
        'r': int(sig['r'], 16),
        's': int(sig['s'], 16),
        'z': int(sig['z'], 16)
    })

# Find signatures with the same r value
r_map = {}
for i, sig in enumerate(sigs):
    r = sig['r']
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with the same r
d = None
for r, indices in r_map.items():
    if len(indices) >= 2:
        i1, i2 = indices[0], indices[1]
        sig1, sig2 = sigs[i1], sigs[i2]
        
        # Calculate k from the two signatures
        z1, s1 = sig1['z'], sig1['s']
        z2, s2 = sig2['z'], sig2['s']
        
        # k = (z1 - z2) / (s1 - s2) mod n
        z_diff = (z1 - z2) % n
        s_diff = (s1 - s2) % n
        
        if s_diff == 0:
            continue
            
        s_diff_inv = modinv(s_diff, n)
        k = (z_diff * s_diff_inv) % n
        
        # Now recover d: d = (s*k - z) / r mod n
        r_inv = modinv(r, n)
        d = ((s1 * k - z1) * r_inv) % n
        
        break

# Format output
d_hex = format(d, '064x')
print(json.dumps({"d": d_hex}))
