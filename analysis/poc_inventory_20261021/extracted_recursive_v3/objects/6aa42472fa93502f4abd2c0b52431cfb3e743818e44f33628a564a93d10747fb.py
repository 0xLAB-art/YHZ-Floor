import json
import sys
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

def recover_private_key(signatures, public_key, n):
    """
    Recover ECDSA private key from signatures with repeated nonces.
    
    Uses the fact that if two signatures share the same r value (same k nonce),
    we can solve for k and then recover the private key d.
    """
    # Group signatures by r value
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append({'s': s, 'z': z})
    
    # Find r values that appear more than once
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            s1, z1 = sigs[0]['s'], sigs[0]['z']
            s2, z2 = sigs[1]['s'], sigs[1]['z']
            
            # From ECDSA: s = k^(-1) * (z + r*d) mod n
            # s1 = k^(-1) * (z1 + r*d) mod n
            # s2 = k^(-1) * (z2 + r*d) mod n
            # Therefore: s1 - s2 = k^(-1) * (z1 - z2) mod n
            # So: k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            try:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Now recover d from: s1 = k^(-1) * (z1 + r*d) mod n
                # s1 * k = z1 + r*d mod n
                # d = (s1*k - z1) / r mod n
                
                k_inv = modinv(k, n)
                r_inv = modinv(r, n)
                d = (r_inv * (s1 * k - z1)) % n
                
                return d, k
            except ValueError:
                continue
    
    return None, None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    public_key = instance['public_key']
    signatures = instance['signatures']
    
    # Recover private key
    d, k = recover_private_key(signatures, public_key, n)
    
    if d is None:
        # Fallback: shouldn't happen with the given data
        d = 0
        k = 0
    
    # Format as 64-character lowercase hex
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()