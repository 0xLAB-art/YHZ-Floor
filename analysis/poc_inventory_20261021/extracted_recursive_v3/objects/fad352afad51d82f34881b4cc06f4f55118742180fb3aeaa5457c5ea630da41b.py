import sys
import json
import hashlib

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
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
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Convert signatures to integers
    sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sigs.append((r, s, z))
    
    # Find duplicate r values
    r_map = {}
    for i, (r, s, z) in enumerate(sigs):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find a pair with the same r
    for r, pairs in r_map.items():
        if len(pairs) >= 2:
            # Use first two signatures with same r
            i1, s1, z1 = pairs[0]
            i2, s2, z2 = pairs[1]
            
            # Recover k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k = (numerator * modinv(denominator, n)) % n
            
            # Recover d: d = (s * k - z) / r mod n
            numerator_d = (s1 * k - z1) % n
            d = (numerator_d * modinv(r, n)) % n
            
            # Format as 64 character hex strings
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            
            print(json.dumps(result))
            return
    
    # Should not reach here if instance is valid
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()