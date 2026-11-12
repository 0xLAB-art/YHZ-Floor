import json
import sys

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
        sigs.append({
            'r': int(sig['r'], 16),
            's': int(sig['s'], 16),
            'z': int(sig['z'], 16)
        })
    
    # Find duplicate r values
    r_map = {}
    for i, sig in enumerate(sigs):
        r = sig['r']
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find a pair with the same r
    k = None
    d = None
    
    for r, indices in r_map.items():
        if len(indices) >= 2:
            # Use first two signatures with same r
            i1, i2 = indices[0], indices[1]
            sig1 = sigs[i1]
            sig2 = sigs[i2]
            
            r = sig1['r']
            s1 = sig1['s']
            s2 = sig2['s']
            z1 = sig1['z']
            z2 = sig2['z']
            
            # Recover k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k = (numerator * modinv(denominator, n)) % n
            
            # Recover d: d = (s * k - z) / r mod n
            numerator = (s1 * k - z1) % n
            denominator = r
            d = (numerator * modinv(denominator, n)) % n
            
            break
    
    # Format output
    k_hex = format(k, '064x')
    d_hex = format(d, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
