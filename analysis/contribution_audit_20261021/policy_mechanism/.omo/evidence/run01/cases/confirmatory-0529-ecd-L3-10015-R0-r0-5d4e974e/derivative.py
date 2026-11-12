import json
import sys


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

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find duplicate r values
    r_to_sigs = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append(i)
    
    # Find a pair with same r
    for r, indices in r_to_sigs.items():
        if len(indices) >= 2:
            i, j = indices[0], indices[1]
            sig1 = signatures[i]
            sig2 = signatures[j]
            
            r_val = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Compute k = (z1 - z2) / (s1 - s2) mod n
            k = ((z1 - z2) * modinv(s1 - s2, n)) % n
            
            # Compute d = (s * k - z) / r mod n
            d = ((s1 * k - z1) * modinv(r_val, n)) % n
            
            # Format as 64 lowercase hex
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            print(json.dumps({"d": d_hex, "k": k_hex}))
            return

if __name__ == '__main__':
    main()
