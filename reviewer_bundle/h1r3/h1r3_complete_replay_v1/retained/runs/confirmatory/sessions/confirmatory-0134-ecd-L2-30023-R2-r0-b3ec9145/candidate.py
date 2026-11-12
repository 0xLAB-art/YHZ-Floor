import sys
import json
import base64
from typing import List, Tuple
from math import gcd

def modinv(a: int, m: int) -> int:
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    if gcd(a, m) != 1:
        raise ValueError("Modular inverse does not exist")
    
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        gcd_val, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd_val, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def recover_private_key_from_nonce_reuse(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> int:
    """
    Recover private key when the same nonce k is used for two signatures.
    
    Given two signatures with the same r value:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    We can solve for k and then d.
    """
    # From the two equations:
    # s1 - s2 = k^-1 * (z1 - z2) mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    
    if s_diff == 0:
        return None
    
    try:
        s_diff_inv = modinv(s_diff, n)
    except ValueError:
        return None
    
    k = (z_diff * s_diff_inv) % n
    
    # Now recover d from: s1 = k^-1 * (z1 + r*d) mod n
    # d = (s1*k - z1) / r mod n
    
    if r == 0:
        return None
    
    try:
        r_inv = modinv(r, n)
    except ValueError:
        return None
    
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA parameters for secp256k1 (standard Bitcoin curve)
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode signatures
    signatures = []
    for sig in instance['signatures']:
        r = int.from_bytes(base64.b64decode(sig['r']), 'big')
        s = int.from_bytes(base64.b64decode(sig['s']), 'big')
        z = int.from_bytes(base64.b64decode(sig['z']), 'big')
        signatures.append((r, s, z))
    
    # Look for nonce reuse (same r value in different signatures)
    d = None
    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            r1, s1, z1 = signatures[i]
            r2, s2, z2 = signatures[j]
            
            if r1 == r2:
                # Found nonce reuse!
                d = recover_private_key_from_nonce_reuse(r1, s1, s2, z1, z2, n)
                if d is not None:
                    break
        if d is not None:
            break
    
    # Format output
    if d is None:
        d = 0
    
    d_hex = format(d, '064x')
    
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
