import sys
import json
import base64


def decode_b64(s):
    return int.from_bytes(base64.b64decode(s), 'big')

def modinv(a, m):
    # Extended Euclidean algorithm
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
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Find duplicate r values
    r_map = {}
    for i, sig in enumerate(signatures):
        r = decode_b64(sig['r'])
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find a pair with same r
    d = None
    k = None
    
    for r_val, indices in r_map.items():
        if len(indices) >= 2:
            i1, i2 = indices[0], indices[1]
            
            r = r_val
            s1 = decode_b64(signatures[i1]['s'])
            z1 = decode_b64(signatures[i1]['z'])
            s2 = decode_b64(signatures[i2]['s'])
            z2 = decode_b64(signatures[i2]['z'])
            
            # Recover k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k = (numerator * modinv(denominator, n)) % n
            
            # Recover d: d = (s*k - z) / r mod n
            numerator = (s1 * k - z1) % n
            denominator = r
            d = (numerator * modinv(denominator, n)) % n
            
            break
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
