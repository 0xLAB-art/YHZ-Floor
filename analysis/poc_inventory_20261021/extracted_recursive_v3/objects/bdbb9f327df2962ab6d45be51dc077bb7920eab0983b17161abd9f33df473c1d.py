import json
import sys
from collections import defaultdict

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def main():
    # SECP256k1 curve parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # Group signatures by r value to find reused nonces
    r_groups = defaultdict(list)
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        r_groups[r].append((i, r, s, z))
    
    # Find pairs with same r (same nonce k)
    d = None
    k = None
    
    for r_val, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            i1, r1, s1, z1 = sigs[0]
            i2, r2, s2, z2 = sigs[1]
            
            # Recover nonce k
            # k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k_recovered = (numerator * modinv(denominator, n)) % n
            
            # Recover private key d
            # d = (s*k - z) / r mod n
            numerator_d = (s1 * k_recovered - z1) % n
            d_recovered = (numerator_d * modinv(r1, n)) % n
            
            # Verify with second signature
            numerator_d2 = (s2 * k_recovered - z2) % n
            d_recovered2 = (numerator_d2 * modinv(r2, n)) % n
            
            if d_recovered == d_recovered2:
                d = d_recovered
                k = k_recovered
                break
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()