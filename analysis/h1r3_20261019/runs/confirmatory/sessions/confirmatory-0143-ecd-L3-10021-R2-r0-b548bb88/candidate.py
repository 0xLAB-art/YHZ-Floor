import sys
import json
import base64
import hashlib

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
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
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # ECDSA uses secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = []
    for sig in data['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # Find duplicate r values (nonce reuse)
    r_to_sigs = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((s, z, i))
    
    # Find a pair with same r
    for r, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            # Use first two signatures with same r
            s1, z1, _ = sig_list[0]
            s2, z2, _ = sig_list[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k = (numerator * modinv(denominator, n)) % n
            
            # d = (s*k - z) / r mod n
            d = ((s1 * k - z1) % n * modinv(r, n)) % n
            
            result = {
                "d": int_to_hex(d),
                "k": int_to_hex(k)
            }
            print(json.dumps(result))
            return
    
    # Should not reach here if nonce reuse exists
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == '__main__':
    main()
