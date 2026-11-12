import sys
import json
import base64
import hashlib

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode public key
    pub_x = int.from_bytes(base64.b64decode(instance['public_key']['x']), 'big')
    pub_y = int.from_bytes(base64.b64decode(instance['public_key']['y']), 'big')
    
    # Decode signatures
    signatures = []
    for sig in instance['signatures']:
        r = int.from_bytes(base64.b64decode(sig['r']), 'big')
        s = int.from_bytes(base64.b64decode(sig['s']), 'big')
        z = int.from_bytes(base64.b64decode(sig['z']), 'big')
        signatures.append((r, s, z))
    
    # Look for repeated r values (nonce reuse)
    r_dict = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_dict:
            r_dict[r] = []
        r_dict[r].append((i, s, z))
    
    # Find pairs with same r
    d = None
    for r, entries in r_dict.items():
        if len(entries) >= 2:
            # Use first two signatures with same r
            i1, s1, z1 = entries[0]
            i2, s2, z2 = entries[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s * k - z) / r mod n
            
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k = (numerator * modinv(denominator, n)) % n
            
            # Now recover d using first signature
            # d = (s1 * k - z1) / r mod n
            d_numerator = (s1 * k - z1) % n
            d = (d_numerator * modinv(r, n)) % n
            
            # Verify with the public key if needed
            break
    
    if d is None:
        # Fallback: try all pairs
        for i in range(len(signatures)):
            for j in range(i + 1, len(signatures)):
                r1, s1, z1 = signatures[i]
                r2, s2, z2 = signatures[j]
                
                if r1 == r2:
                    numerator = (z1 - z2) % n
                    denominator = (s1 - s2) % n
                    
                    if denominator == 0:
                        continue
                    
                    k = (numerator * modinv(denominator, n)) % n
                    d_numerator = (s1 * k - z1) % n
                    d = (d_numerator * modinv(r1, n)) % n
                    break
            
            if d is not None:
                break
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()