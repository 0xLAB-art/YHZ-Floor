import sys
import json
import hashlib

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(r, s1, s2, z1, z2, n):
    """Recover private key from two signatures with same r (same k)"""
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None, None
    
    k = (numerator * modinv(denominator, n)) % n
    
    # d = (s*k - z) / r mod n
    d = ((s1 * k - z1) % n * modinv(r, n)) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # secp256k1 order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Convert signatures to integers
    sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sigs.append((r, s, z))
    
    # Find signatures with the same r value
    r_groups = {}
    for i, (r, s, z) in enumerate(sigs):
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append((i, s, z))
    
    # Find a pair with same r
    d = None
    k = None
    
    for r, group in r_groups.items():
        if len(group) >= 2:
            # Use first two signatures with same r
            idx1, s1, z1 = group[0]
            idx2, s2, z2 = group[1]
            
            d, k = recover_private_key(r, s1, s2, z1, z2, n)
            
            if d is not None and k is not None:
                break
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()