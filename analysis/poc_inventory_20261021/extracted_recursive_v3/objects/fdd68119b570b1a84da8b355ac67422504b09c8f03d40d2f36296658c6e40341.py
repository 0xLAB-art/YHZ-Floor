import sys
import json
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

def recover_private_key_from_nonce_reuse(
    r: int, s1: int, s2: int, z1: int, z2: int, n: int
) -> int:
    """
    Recover private key when the same nonce k is used in two signatures.
    
    From ECDSA equations:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    Solving for k:
    k = (z1 - z2) / (s1 - s2) mod n
    
    Then solving for d:
    d = (s*k - z) / r mod n
    """
    # Calculate k from the two signatures
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        raise ValueError("s1 and s2 are equal, cannot recover nonce")
    
    k = (numerator * modinv(denominator, n)) % n
    
    # Calculate private key d from k
    d = (((s1 * k - z1) % n) * modinv(r, n)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Look for signature pairs with the same r value (nonce reuse)
    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            r1 = int(signatures[i]['r'], 16)
            r2 = int(signatures[j]['r'], 16)
            
            if r1 == r2:
                # Found nonce reuse!
                s1 = int(signatures[i]['s'], 16)
                s2 = int(signatures[j]['s'], 16)
                z1 = int(signatures[i]['z'], 16)
                z2 = int(signatures[j]['z'], 16)
                
                try:
                    d = recover_private_key_from_nonce_reuse(r1, s1, s2, z1, z2, n)
                    
                    # Format as 64 lowercase hex characters
                    d_hex = format(d, '064x')
                    
                    print(json.dumps({"d": d_hex}))
                    return
                except:
                    continue
    
    # If no nonce reuse found, output error (shouldn't happen with valid input)
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()