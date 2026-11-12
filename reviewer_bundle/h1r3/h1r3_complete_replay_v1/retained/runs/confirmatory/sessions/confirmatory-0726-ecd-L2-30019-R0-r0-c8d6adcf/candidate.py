import sys
import json
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

def recover_private_key(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> int:
    """
    Recover private key when the same r (nonce k) is used in two signatures.
    
    From ECDSA equations:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    Solving:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1*k - z1) / r mod n
    """
    # Calculate k from the two signatures
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    k = (numerator * modinv(denominator, n)) % n
    
    # Calculate private key d
    d_numerator = (s1 * k - z1) % n
    d = (d_numerator * modinv(r, n)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find signatures with the same r value
    r_map = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((s, z))
    
    # Find r values that appear more than once
    for r, sig_list in r_map.items():
        if len(sig_list) >= 2:
            # Use first two signatures with same r
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            # Recover private key
            d = recover_private_key(r, s1, s2, z1, z2, n)
            
            # Format as 64 lowercase hex characters
            d_hex = format(d, '064x')
            
            print(json.dumps({"d": d_hex}))
            return
    
    # If no matching r found, output error (shouldn't happen with valid input)
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()
