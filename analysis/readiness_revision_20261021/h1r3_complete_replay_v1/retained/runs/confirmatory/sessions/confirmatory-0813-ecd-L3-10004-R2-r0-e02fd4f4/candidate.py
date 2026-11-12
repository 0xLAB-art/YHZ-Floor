import sys
import json
import base64
import hashlib

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
    """Convert bytes to integer"""
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    """Convert integer to 64-character lowercase hex string"""
    return format(n, '064x')

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode signatures
    signatures = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # Find signatures with same r value
    r_dict = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_dict:
            r_dict[r] = []
        r_dict[r].append((i, s, z))
    
    # Find pair with same r
    d = None
    k = None
    for r, pairs in r_dict.items():
        if len(pairs) >= 2:
            # Use first two signatures with same r
            i1, s1, z1 = pairs[0]
            i2, s2, z2 = pairs[1]
            
            # Recover nonce k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k = (numerator * modinv(denominator, n)) % n
            
            # Recover private key d: d = (s * k - z) / r mod n
            numerator = (s1 * k - z1) % n
            denominator = r
            d = (numerator * modinv(denominator, n)) % n
            
            break
    
    # Output result
    result = {
        "d": int_to_hex(d),
        "k": int_to_hex(k)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
