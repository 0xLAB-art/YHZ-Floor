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

def recover_private_key(r1: int, s1: int, z1: int, r2: int, s2: int, z2: int, n: int) -> int:
    """
    Recover private key from two signatures with the same nonce k.
    
    From ECDSA:
    s1 = k^(-1) * (z1 + r1 * d) mod n
    s2 = k^(-1) * (z2 + r2 * d) mod n
    
    If r1 == r2, then same k was used.
    s1 - s2 = k^(-1) * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    
    Then: d = (s1 * k - z1) / r1 mod n
    """
    # Calculate k
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None
    
    k = (numerator * modinv(denominator, n)) % n
    
    # Calculate d (private key)
    d = ((s1 * k - z1) * modinv(r1, n)) % n
    
    return d

def find_duplicate_r(signatures: List[dict]) -> Tuple[int, int]:
    """Find indices of two signatures with the same r value."""
    r_map = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r in r_map:
            return r_map[r], i
        r_map[r] = i
    return None, None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with duplicate r values
    idx1, idx2 = find_duplicate_r(signatures)
    
    if idx1 is not None and idx2 is not None:
        sig1 = signatures[idx1]
        sig2 = signatures[idx2]
        
        r1 = int(sig1['r'], 16)
        s1 = int(sig1['s'], 16)
        z1 = int(sig1['z'], 16)
        
        r2 = int(sig2['r'], 16)
        s2 = int(sig2['s'], 16)
        z2 = int(sig2['z'], 16)
        
        # Recover private key
        d = recover_private_key(r1, s1, z1, r2, s2, z2, n)
        
        if d is not None:
            # Recover k from the first signature
            k = ((z1 + r1 * d) * modinv(s1, n)) % n
            
            # Format output
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            
            print(json.dumps(result))

if __name__ == "__main__":
    main()