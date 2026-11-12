import json
import sys
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

def bytes_to_int(b):
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
    y = bytes_to_int(base64.b64decode(instance['public_key']['y']))
    
    # Parse signatures
    sigs = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        sigs.append((r, s, z))
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Extract two signatures with same r
    r1, s1, z1 = sigs[0]
    r2, s2, z2 = sigs[1]
    
    # Check if r values are the same (nonce reuse attack)
    if r1 == r2:
        # k = (z1 - z2) / (s1 - s2) mod n
        # d = (s*k - z) / r mod n
        
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        
        k = (numerator * modinv(denominator, n)) % n
        
        # Now recover private key d
        # s1 = (z1 + r1*d) / k mod n
        # s1*k = z1 + r1*d mod n
        # r1*d = s1*k - z1 mod n
        # d = (s1*k - z1) / r1 mod n
        
        numerator_d = (s1 * k - z1) % n
        d = (numerator_d * modinv(r1, n)) % n
        
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        
        result = {"d": d_hex}
        print(json.dumps(result))

if __name__ == "__main__":
    main()
