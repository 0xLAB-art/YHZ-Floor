import json
import sys
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

def recover_private_key(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> int:
    """
    Recover private key from two signatures with the same r value (same k nonce).
    
    From ECDSA:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    Therefore:
    s1 - s2 = k^(-1) * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    
    Then:
    d = (s1*k - z1) / r mod n
    """
    # Calculate k
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d (private key)
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # SECP256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Parse signatures
    parsed_sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        parsed_sigs.append((r, s, z))
    
    # Find two signatures with the same r value
    r_map = {}
    for i, (r, s, z) in enumerate(parsed_sigs):
        if r in r_map:
            # Found a duplicate r value
            j = r_map[r]
            r1, s1, z1 = parsed_sigs[j]
            r2, s2, z2 = parsed_sigs[i]
            
            # Recover private key
            d = recover_private_key(r1, s1, s2, z1, z2, n)
            
            # Format as 64 lowercase hex characters
            d_hex = format(d, '064x')
            
            result = {"d": d_hex}
            print(json.dumps(result))
            return
        else:
            r_map[r] = i
    
    # If no duplicate found, should not happen based on problem setup
    raise ValueError("No duplicate r values found")

if __name__ == "__main__":
    main()