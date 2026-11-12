import sys
import json
import base64


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

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex64(n):
    return format(n, '064x')

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    sigs = []
    for sig in data['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        sigs.append((r, s, z))
    
    # Find duplicate r values (nonce reuse)
    r_map = {}
    for i, (r, s, z) in enumerate(sigs):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find a pair with same r
    d = None
    k = None
    
    for r, sig_list in r_map.items():
        if len(sig_list) >= 2:
            # Use first two signatures with same r
            i1, s1, z1 = sig_list[0]
            i2, s2, z2 = sig_list[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k_candidate = (numerator * modinv(denominator, n)) % n
            
            # d = (s*k - z) / r mod n
            d_candidate = ((s1 * k_candidate - z1) % n * modinv(r, n)) % n
            
            # Verify with another signature
            verify_works = True
            for r_check, s_check, z_check in sigs[:3]:
                k_check = (z_check + r_check * d_candidate) % n * modinv(s_check, n) % n
                if k_check == 0:
                    verify_works = False
                    break
            
            if verify_works:
                d = d_candidate
                k = k_candidate
                break
    
    result = {
        "d": int_to_hex64(d),
        "k": int_to_hex64(k)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
