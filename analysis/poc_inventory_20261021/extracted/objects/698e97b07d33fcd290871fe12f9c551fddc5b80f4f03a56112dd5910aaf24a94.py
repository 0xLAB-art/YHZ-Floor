import json
import sys
import base64
from hashlib import sha256

def mod_inverse(a, m):
    """Compute modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode public key
    pub_x = int.from_bytes(base64.b64decode(instance['public_key']['x']), 'big')
    pub_y = int.from_bytes(base64.b64decode(instance['public_key']['y']), 'big')
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode signatures
    sigs = []
    for sig in instance['signatures']:
        r = int.from_bytes(base64.b64decode(sig['r']), 'big')
        s = int.from_bytes(base64.b64decode(sig['s']), 'big')
        z = int.from_bytes(base64.b64decode(sig['z']), 'big')
        sigs.append((r, s, z))
    
    # Find two signatures with the same r value (nonce reuse)
    r_groups = {}
    for i, (r, s, z) in enumerate(sigs):
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append((i, s, z))
    
    # Find a repeated r with at least 2 signatures
    d = None
    for r, group in r_groups.items():
        if len(group) >= 2:
            # Use first two signatures with same r
            s1, z1 = group[0][1], group[0][2]
            s2, z2 = group[1][1], group[1][2]
            
            # Recover nonce k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k = (numerator * mod_inverse(denominator, n)) % n
            
            if k == 0:
                continue
            
            # Recover private key: d = (s*k - z) / r mod n
            d = ((s1 * k - z1) * mod_inverse(r, n)) % n
            
            if d != 0:
                break
    
    if d is None:
        # Fallback: shouldn't happen with proper nonce reuse
        d = 0
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
