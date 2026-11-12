import json
import sys
import base64
from typing import List, Tuple

def modinv(a: int, m: int) -> int:
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
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

def decode_base64_int(s: str) -> int:
    """Decode base64 string to integer."""
    data = base64.b64decode(s)
    return int.from_bytes(data, 'big')

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode public key
    Qx = decode_base64_int(instance['public_key']['x'])
    Qy = decode_base64_int(instance['public_key']['y'])
    
    # Decode signatures
    signatures = []
    for sig in instance['signatures']:
        r = decode_base64_int(sig['r'])
        s = decode_base64_int(sig['s'])
        z = decode_base64_int(sig['z'])
        signatures.append((r, s, z))
    
    # Look for repeated r values (nonce reuse attack)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find pairs with same r
    for r, occurrences in r_map.items():
        if len(occurrences) >= 2:
            # Use first two occurrences
            i1, s1, z1 = occurrences[0]
            i2, s2, z2 = occurrences[1]
            
            # Recover private key using nonce reuse
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s1 * k - z1) / r mod n
            
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k = (numerator * modinv(denominator, n)) % n
            
            # Now compute d
            d_numerator = (s1 * k - z1) % n
            d_denominator = r % n
            
            if d_denominator == 0:
                continue
            
            d = (d_numerator * modinv(d_denominator, n)) % n
            
            # Format as 64 lowercase hex characters
            d_hex = format(d, '064x')
            
            result = {"d": d_hex}
            print(json.dumps(result))
            return

if __name__ == "__main__":
    main()