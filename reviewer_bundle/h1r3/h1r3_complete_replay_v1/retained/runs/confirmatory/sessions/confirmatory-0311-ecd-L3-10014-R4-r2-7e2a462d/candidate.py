import sys
import json
from typing import Tuple

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

def solve_ecdsa_nonce_reuse(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> int:
    """
    Recover private key when nonce k is reused in two signatures.
    
    From ECDSA equations:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    Solving:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1*k - z1) / r mod n
    """
    # Compute k from the two signatures
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        raise ValueError("Cannot recover: s1 == s2")
    
    k = (numerator * modinv(denominator, n)) % n
    
    # Compute private key d from k
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find signatures with the same r value (nonce reuse)
    r_map = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((s, z))
    
    # Find a pair with reused nonce
    for r, sig_list in r_map.items():
        if len(sig_list) >= 2:
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            try:
                d, k = solve_ecdsa_nonce_reuse(r, s1, s2, z1, z2, n)
                
                # Format output
                d_hex = format(d, '064x')
                k_hex = format(k, '064x')
                
                result = {
                    "d": d_hex,
                    "k": k_hex
                }
                
                print(json.dumps(result))
                return
            except:
                continue
    
    # Should not reach here if instance is valid
    raise ValueError("No nonce reuse found")

if __name__ == "__main__":
    main()
