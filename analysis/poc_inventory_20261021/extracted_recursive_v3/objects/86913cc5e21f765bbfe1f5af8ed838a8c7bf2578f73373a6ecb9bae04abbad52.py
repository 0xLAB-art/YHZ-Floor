import sys
import json
import base64
import hashlib

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

def modinv(a, m):
    """Extended Euclidean Algorithm for modular inverse"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # Decode public key
    pub_x = bytes_to_int(base64.b64decode(data['public_key']['x']))
    pub_y = bytes_to_int(base64.b64decode(data['public_key']['y']))
    
    # Decode signatures
    sigs = []
    for sig in data['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        sigs.append((r, s, z))
    
    # Look for duplicate r values (nonce reuse)
    r_map = {}
    for i, (r, s, z) in enumerate(sigs):
        if r in r_map:
            r_map[r].append((i, s, z))
        else:
            r_map[r] = [(i, s, z)]
    
    # Find a pair with the same r
    for r, entries in r_map.items():
        if len(entries) >= 2:
            # We have nonce reuse!
            i1, s1, z1 = entries[0]
            i2, s2, z2 = entries[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k = (numerator * modinv(denominator, n)) % n
            
            # d = (s1 * k - z1) / r mod n
            numerator2 = (s1 * k - z1) % n
            d = (numerator2 * modinv(r, n)) % n
            
            # Output the result
            result = {
                "d": int_to_hex(d),
                "k": int_to_hex(k)
            }
            print(json.dumps(result))
            return
    
    # Should not reach here if the problem is solvable
    result = {
        "d": "0" * 64,
        "k": "0" * 64
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()