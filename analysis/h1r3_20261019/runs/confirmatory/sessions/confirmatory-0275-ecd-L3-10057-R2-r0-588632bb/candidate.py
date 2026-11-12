import sys
import json
import base64
import hashlib

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
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
        instance = json.load(f)
    
    # Decode public key
    pub_x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
    pub_y = bytes_to_int(base64.b64decode(instance['public_key']['y']))
    
    # Decode signatures
    sigs = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        sigs.append((r, s, z))
    
    # Look for repeated r values (nonce reuse)
    r_dict = {}
    for i, (r, s, z) in enumerate(sigs):
        if r not in r_dict:
            r_dict[r] = []
        r_dict[r].append((i, s, z))
    
    # Find nonce reuse
    k = None
    d = None
    
    for r, entries in r_dict.items():
        if len(entries) >= 2:
            # Nonce reuse detected
            i1, s1, z1 = entries[0]
            i2, s2, z2 = entries[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k_candidate = (numerator * modinv(denominator, n)) % n
            
            # Verify and recover d
            # s = (z + r*d) / k mod n
            # d = (s*k - z) / r mod n
            r_inv = modinv(r, n)
            d_candidate = ((s1 * k_candidate - z1) * r_inv) % n
            
            # Verify with second signature
            expected_s2 = ((z2 + r * d_candidate) * modinv(k_candidate, n)) % n
            if expected_s2 == s2:
                k = k_candidate
                d = d_candidate
                break
    
    # Output
    result = {
        "d": int_to_hex(d),
        "k": int_to_hex(k)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
