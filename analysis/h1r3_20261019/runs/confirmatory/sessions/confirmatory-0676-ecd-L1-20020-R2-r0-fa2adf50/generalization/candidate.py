import sys
import json
import base64
from typing import Tuple

def mod_inverse(a: int, m: int) -> int:
    """Compute modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> int:
    """
    Recover private key from two signatures with the same r value (nonce reuse).
    
    Given:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    We can solve for k and then d.
    """
    # s1 - s2 = k^(-1) * (z1 - z2) mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = mod_inverse(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Now recover d from: s1 = k^(-1) * (z1 + r*d) mod n
    # s1 * k = z1 + r*d mod n
    # d = (s1*k - z1) / r mod n
    
    r_inv = mod_inverse(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # NIST P-256 (secp256r1) curve order
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Decode public key (not needed for this attack but included for completeness)
    x = int.from_bytes(base64.b64decode(instance['public_key']['x']), 'big')
    y = int.from_bytes(base64.b64decode(instance['public_key']['y']), 'big')
    
    # Decode signatures
    sig1 = instance['signatures'][0]
    sig2 = instance['signatures'][1]
    
    r1 = int.from_bytes(base64.b64decode(sig1['r']), 'big')
    s1 = int.from_bytes(base64.b64decode(sig1['s']), 'big')
    z1 = int.from_bytes(base64.b64decode(sig1['z']), 'big')
    
    r2 = int.from_bytes(base64.b64decode(sig2['r']), 'big')
    s2 = int.from_bytes(base64.b64decode(sig2['s']), 'big')
    z2 = int.from_bytes(base64.b64decode(sig2['z']), 'big')
    
    # Check if r values are the same (nonce reuse vulnerability)
    if r1 == r2:
        # Recover private key
        d = recover_private_key(r1, s1, s2, z1, z2, n)
        
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        
        # Output result
        result = {"d": d_hex}
        print(json.dumps(result))
    else:
        raise ValueError("Different r values - cannot exploit nonce reuse")

if __name__ == "__main__":
    main()
