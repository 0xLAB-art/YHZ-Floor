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
    s1 = k^(-1) * (z1 + r * d) mod n
    s2 = k^(-1) * (z2 + r * d) mod n
    
    Solving for d:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1 * k - z1) / r mod n
    """
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    # k = (z1 - z2) / (s1 - s2) mod n
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # d = (s * k - z) / r mod n
    r_inv = modinv(r, n)
    d = (((s1 * k - z1) % n) * r_inv) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    pub_x = int(instance['public_key']['x'], 16)
    pub_y = int(instance['public_key']['y'], 16)
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Look for nonce reuse: same r value in different signatures
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_map:
            # Found nonce reuse!
            j = r_map[r]
            r1, s1, z1 = signatures[j]
            r2, s2, z2 = signatures[i]
            
            # Recover private key
            d = recover_private_key_from_nonce_reuse(r1, s1, s2, z1, z2, n)
            
            # Format as 64 lowercase hex characters
            d_hex = format(d, '064x')
            
            # Output result
            result = {"d": d_hex}
            print(json.dumps(result))
            return
        else:
            r_map[r] = i
    
    # If no nonce reuse found, this shouldn't happen based on the problem
    raise ValueError("No nonce reuse detected")

if __name__ == "__main__":
    main()