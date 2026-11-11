import sys
import json
import base64
from typing import Tuple, Optional

def modinv(a: int, m: int) -> int:
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

def recover_private_key_from_nonce_reuse(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> Optional[int]:
    """
    Recover private key when the same nonce k is used for two signatures.
    
    Given: r, s1, s2, z1, z2, and curve order n
    We have:
        s1 = k^-1 * (z1 + r*d) mod n
        s2 = k^-1 * (z2 + r*d) mod n
    
    From these equations:
        k = (z1 - z2) / (s1 - s2) mod n
        d = (s1*k - z1) / r mod n
    """
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    if s_diff == 0:
        return None
    
    try:
        k = (z_diff * modinv(s_diff, n)) % n
        d = (((s1 * k - z1) % n) * modinv(r, n)) % n
        return d
    except ValueError:
        return None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # NIST P-256 curve order
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = int.from_bytes(base64.b64decode(sig['r']), 'big')
        s = int.from_bytes(base64.b64decode(sig['s']), 'big')
        z = int.from_bytes(base64.b64decode(sig['z']), 'big')
        signatures.append((r, s, z))
    
    # Look for signature pairs with the same r value (nonce reuse)
    d = None
    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            r1, s1, z1 = signatures[i]
            r2, s2, z2 = signatures[j]
            
            if r1 == r2:
                # Same nonce used, we can recover the private key
                d = recover_private_key_from_nonce_reuse(r1, s1, s2, z1, z2, n)
                if d is not None:
                    break
        if d is not None:
            break
    
    # Format output
    d_hex = format(d, '064x')
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
