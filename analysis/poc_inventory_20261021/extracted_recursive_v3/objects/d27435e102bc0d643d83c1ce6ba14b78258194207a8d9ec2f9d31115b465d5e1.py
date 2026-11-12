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
    Recover private key from two signatures with the same nonce (same r value).
    
    From ECDSA equations:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    Solving for k:
    k = (z1 - z2) / (s1 - s2) mod n
    
    Then solving for d:
    d = (s1*k - z1) / r mod n
    """
    # Calculate k from the two signatures
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None
    
    k = (numerator * modinv(denominator, n)) % n
    
    if k == 0:
        return None
    
    # Calculate private key d
    d_numerator = (s1 * k - z1) % n
    d_denominator = r % n
    
    if d_denominator == 0:
        return None
    
    d = (d_numerator * modinv(d_denominator, n)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Look for signatures with the same r value (nonce reuse)
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r in r_map:
            # Found nonce reuse!
            prev_i, prev_s, prev_z = r_map[r]
            
            # Try to recover the private key
            d = recover_private_key_from_nonce_reuse(r, prev_s, s, prev_z, z, n)
            
            if d is not None and d != 0:
                # We found the private key, now recover k from one of the signatures
                # k = (z + r*d) / s mod n
                k = ((prev_z + r * d) * modinv(prev_s, n)) % n
                
                # Format output
                d_hex = format(d, '064x')
                k_hex = format(k, '064x')
                
                result = {
                    "d": d_hex,
                    "k": k_hex
                }
                
                print(json.dumps(result))
                return
        else:
            r_map[r] = (i, s, z)
    
    # Should not reach here if there's nonce reuse
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()