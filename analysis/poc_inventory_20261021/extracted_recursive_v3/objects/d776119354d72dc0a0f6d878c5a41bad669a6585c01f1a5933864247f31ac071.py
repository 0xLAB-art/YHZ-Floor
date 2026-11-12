import sys
import json
from typing import Tuple, Optional

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

def recover_private_key_ecdsa(
    signatures: list,
    n: int
) -> Optional[Tuple[int, int]]:
    """
    Recover ECDSA private key from signatures with repeated nonce.
    
    For two signatures with same r (same k):
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    Then: k = (z1 - z2) / (s1 - s2) mod n
    And: d = (s*k - z) / r mod n
    """
    # Group signatures by r value
    r_groups = {}
    for sig in signatures:
        r = sig['r']
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(sig)
    
    # Find signatures with repeated r
    for r_val, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1, sig2 = sigs[0], sigs[1]
            r = int(r_val, 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Calculate k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            try:
                k = (numerator * modinv(denominator, n)) % n
                
                # Calculate d = (s*k - z) / r mod n
                numerator_d = (s1 * k - z1) % n
                d = (numerator_d * modinv(r, n)) % n
                
                return d, k
            except ValueError:
                continue
    
    return None

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Recover private key
    result = recover_private_key_ecdsa(signatures, n)
    
    if result:
        d, k = result
        # Format as 64 character lowercase hex
        d_hex = format(d, '064x')
        k_hex = format(k, '064x')
        
        output = {
            "d": d_hex,
            "k": k_hex
        }
        print(json.dumps(output))
    else:
        # Fallback (should not reach here with valid input)
        print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()