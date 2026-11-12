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
    Recover private key when the same nonce k is used for two signatures.
    
    From ECDSA equations:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    We can solve for k and then d.
    """
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None
    
    k = (numerator * modinv(denominator, n)) % n
    
    # Now recover d from: s1 = k^-1 * (z1 + r*d) mod n
    # => s1 * k = z1 + r*d mod n
    # => d = (s1*k - z1) / r mod n
    
    numerator_d = (s1 * k - z1) % n
    d = (numerator_d * modinv(r, n)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # Look for nonce reuse (same r value)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find pairs with same r
    private_key = None
    for r, sigs in r_map.items():
        if len(sigs) >= 2:
            # We have nonce reuse!
            idx1, s1, z1 = sigs[0]
            idx2, s2, z2 = sigs[1]
            
            # Try to recover the private key
            d = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
            
            if d is not None:
                private_key = d
                break
    
    # Format output
    if private_key is not None:
        result = {"d": format(private_key, '064x')}
    else:
        result = {"d": "0" * 64}
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()