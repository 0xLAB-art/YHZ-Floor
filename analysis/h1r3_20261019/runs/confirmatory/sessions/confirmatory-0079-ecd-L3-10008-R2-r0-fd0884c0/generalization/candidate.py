import sys
import json
import base64
import hashlib

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex64(n):
    return format(n, '064x')

def modinv(a, m):
    """Extended Euclidean algorithm for modular inverse"""
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
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find duplicate r values
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_map:
            r_map[r].append((s, z, i))
        else:
            r_map[r] = [(s, z, i)]
    
    # Find a pair with same r
    for r, sigs in r_map.items():
        if len(sigs) >= 2:
            s1, z1, _ = sigs[0]
            s2, z2, _ = sigs[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k = (numerator * modinv(denominator, n)) % n
            
            if k == 0:
                continue
            
            # d = (s1*k - z1) / r mod n
            k_inv = modinv(k, n)
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            # Output result
            result = {
                "d": int_to_hex64(d),
                "k": int_to_hex64(k)
            }
            print(json.dumps(result))
            return
    
    # Fallback (should not reach here if valid duplicate exists)
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()
