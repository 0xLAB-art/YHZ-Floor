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

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find duplicate r values
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r in r_map:
            # Found duplicate - recover k and d
            j = r_map[r]
            
            r_val = r
            s1 = int(signatures[j]['s'], 16)
            z1 = int(signatures[j]['z'], 16)
            s2 = int(sig['s'], 16)
            z2 = int(sig['z'], 16)
            
            # Recover k: k = (z1 - z2) * (s1 - s2)^(-1) mod n
            z_diff = (z1 - z2) % n
            s_diff = (s1 - s2) % n
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Recover d: d = (s*k - z) * r^(-1) mod n
            r_inv = modinv(r_val, n)
            d = ((s1 * k - z1) * r_inv) % n
            
            # Format as 64 hex characters
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            print(json.dumps(result))
            return
        else:
            r_map[r] = i

if __name__ == '__main__':
    main()
