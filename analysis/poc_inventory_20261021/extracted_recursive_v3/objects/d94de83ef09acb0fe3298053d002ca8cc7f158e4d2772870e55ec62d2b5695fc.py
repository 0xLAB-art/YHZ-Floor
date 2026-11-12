import json
import sys

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

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find duplicate r values
    r_to_sigs = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append(i)
    
    # Find a duplicate r
    for r, indices in r_to_sigs.items():
        if len(indices) >= 2:
            # Use first two signatures with same r
            i1, i2 = indices[0], indices[1]
            sig1 = signatures[i1]
            sig2 = signatures[i2]
            
            r_val = r
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Recover k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k = (numerator * modinv(denominator, n)) % n
            
            # Recover d: d = (s1*k - z1) / r mod n
            numerator_d = (s1 * k - z1) % n
            d = (numerator_d * modinv(r_val, n)) % n
            
            # Format output
            result = {
                "d": format(d, '064x'),
                "k": format(k, '064x')
            }
            
            print(json.dumps(result))
            return

if __name__ == '__main__':
    main()