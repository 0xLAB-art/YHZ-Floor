import json
import sys
import base64
from typing import Tuple

def modinv(a: int, m: int) -> int:
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean algorithm. Returns (gcd, x, y) such that ax + by = gcd."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def decode_b64_to_int(s: str) -> int:
    """Decode base64 string to integer."""
    return int.from_bytes(base64.b64decode(s), 'big')

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # Parse public key
    x = decode_b64_to_int(data['public_key']['x'])
    y = decode_b64_to_int(data['public_key']['y'])
    
    # Parse signatures
    sigs = []
    for sig in data['signatures']:
        r = decode_b64_to_int(sig['r'])
        s = decode_b64_to_int(sig['s'])
        z = decode_b64_to_int(sig['z'])
        sigs.append((r, s, z))
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
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
        # d = (s1*k - z1) / r1 mod n
        numerator_d = (s1 * k - z1) % n
        d = (numerator_d * modinv(r1, n)) % n
        
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        
        print(json.dumps({"d": d_hex}))

if __name__ == "__main__":
    main()