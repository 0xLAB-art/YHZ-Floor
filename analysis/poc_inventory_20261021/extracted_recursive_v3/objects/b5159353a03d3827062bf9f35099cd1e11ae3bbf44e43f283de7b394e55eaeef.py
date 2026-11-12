import json
import sys

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
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

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find duplicate r values
    r_map = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find a pair with the same r
    for r_hex, indices in r_map.items():
        if len(indices) >= 2:
            i1, i2 = indices[0], indices[1]
            
            r = int(r_hex, 16)
            s1 = int(signatures[i1]['s'], 16)
            s2 = int(signatures[i2]['s'], 16)
            z1 = int(signatures[i1]['z'], 16)
            z2 = int(signatures[i2]['z'], 16)
            
            # Recover k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k = (numerator * modinv(denominator, n)) % n
            
            # Recover d: d = (s*k - z) / r mod n
            numerator = (s1 * k - z1) % n
            d = (numerator * modinv(r, n)) % n
            
            # Format output
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            print(json.dumps({"d": d_hex, "k": k_hex}))
            return

if __name__ == "__main__":
    main()