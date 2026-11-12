import sys
import json
from typing import List, Tuple, Optional

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

def recover_private_key_from_reused_k(
    r1: int, s1: int, z1: int,
    r2: int, s2: int, z2: int,
    n: int
) -> Optional[int]:
    """
    Recover private key when the same k (nonce) is used for two signatures.
    
    ECDSA signature equations:
    s1 = k^(-1) * (z1 + r1 * d) mod n
    s2 = k^(-1) * (z2 + r2 * d) mod n
    
    When r1 == r2, the same k was used.
    
    From these equations:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1 * k - z1) / r1 mod n
    """
    if r1 != r2:
        return None
    
    # Calculate k
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None
    
    try:
        k = (numerator * modinv(denominator, n)) % n
    except ValueError:
        return None
    
    # Calculate private key d
    try:
        d = ((s1 * k - z1) * modinv(r1, n)) % n
    except ValueError:
        return None
    
    return d

def find_nonce_reuse_and_recover_key(signatures: List[dict], n: int) -> Optional[Tuple[int, int]]:
    """
    Find two signatures with the same r value (indicating nonce reuse) 
    and recover the private key and nonce.
    """
    # Group signatures by r value
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append((s, z))
    
    # Find pairs with same r
    for r, sig_list in r_groups.items():
        if len(sig_list) >= 2:
            # Try the first two signatures with this r
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            d = recover_private_key_from_reused_k(r, s1, z1, r, s2, z2, n)
            if d is not None:
                # Recover k from the first signature
                try:
                    k = ((z1 + r * d) * modinv(s1, n)) % n
                    return d, k
                except ValueError:
                    continue
    
    return None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    result = find_nonce_reuse_and_recover_key(signatures, n)
    
    if result:
        d, k = result
        # Format as 64-character lowercase hex
        d_hex = format(d, '064x')
        k_hex = format(k, '064x')
        
        output = {
            "d": d_hex,
            "k": k_hex
        }
        print(json.dumps(output))
    else:
        # Should not happen with valid input, but provide fallback
        print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()
