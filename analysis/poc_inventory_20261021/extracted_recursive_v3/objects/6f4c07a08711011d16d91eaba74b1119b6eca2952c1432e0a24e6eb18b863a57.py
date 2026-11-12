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

def recover_key_from_reused_nonce(r, s1, z1, s2, z2, n):
    """Recover private key when nonce is reused"""
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # d = (s*k - z) / r mod n
    numerator = (s1 * k - z1) % n
    d = (numerator * modinv(r, n)) % n
    
    return d, k

# SECP256k1 parameters
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

signatures = data['signatures']

# Convert signatures to integers
sigs = []
for sig in signatures:
    sigs.append({
        'r': int(sig['r'], 16),
        's': int(sig['s'], 16),
        'z': int(sig['z'], 16)
    })

# Find duplicate r values
r_map = {}
for i, sig in enumerate(sigs):
    r = sig['r']
    if r in r_map:
        # Found reused nonce!
        j = r_map[r]
        sig1 = sigs[j]
        sig2 = sigs[i]
        
        d, k = recover_key_from_reused_nonce(
            sig1['r'],
            sig1['s'],
            sig1['z'],
            sig2['s'],
            sig2['z'],
            n
        )
        
        # Format output
        d_hex = format(d, '064x')
        k_hex = format(k, '064x')
        
        print(json.dumps({"d": d_hex, "k": k_hex}))
        break
    else:
        r_map[r] = i
