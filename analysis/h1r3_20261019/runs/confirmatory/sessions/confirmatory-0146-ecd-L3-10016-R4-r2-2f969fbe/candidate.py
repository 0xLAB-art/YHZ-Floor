import sys
import json
from typing import List, Tuple

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

def recover_private_key(signatures: List[dict], n: int) -> int:
    """
    Recover ECDSA private key from signatures with repeated nonce (r value).
    
    ECDSA signature equations:
    s = k^(-1) * (z + r*d) mod n
    
    For two signatures with same k (same r):
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    From these we can derive:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    
    # Group signatures by r value to find repeated nonces
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(sig)
    
    # Find r values that appear more than once
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1 = sigs[0]
            sig2 = sigs[1]
            
            r_val = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Calculate k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
                
            k = (numerator * modinv(denominator, n)) % n
            
            # Calculate d: d = (s*k - z) / r mod n
            numerator_d = (s1 * k - z1) % n
            d = (numerator_d * modinv(r_val, n)) % n
            
            # Verify with the second signature
            numerator_d2 = (s2 * k - z2) % n
            d2 = (numerator_d2 * modinv(r_val, n)) % n
            
            if d == d2 and d != 0:
                return d, k
    
    raise ValueError("Could not recover private key")

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Recover private key and nonce
    d, k = recover_private_key(signatures, n)
    
    # Format output as 64 lowercase hex characters
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
