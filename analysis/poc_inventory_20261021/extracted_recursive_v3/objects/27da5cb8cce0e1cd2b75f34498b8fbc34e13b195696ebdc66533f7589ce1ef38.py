import json
import sys
import hashlib
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

def base64_to_int(b64_str: str) -> int:
    """Convert base64 string to integer."""
    import base64
    decoded = base64.b64decode(b64_str)
    return int.from_bytes(decoded, byteorder='big')

def recover_private_key(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> int:
    """
    Recover private key from two signatures with the same r value (nonce reuse).
    
    From ECDSA equations:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    We can derive:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1*k - z1) / r mod n
    """
    # Calculate k from the two signatures
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # Calculate private key d
    numerator_d = (s1 * k - z1) % n
    d = (numerator_d * modinv(r, n)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = base64_to_int(sig['r'])
        s = base64_to_int(sig['s'])
        z = base64_to_int(sig['z'])
        signatures.append({'r': r, 's': s, 'z': z})
    
    # NIST P-256 curve order
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Find signatures with the same r value (nonce reuse vulnerability)
    r_groups = {}
    for sig in signatures:
        r = sig['r']
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(sig)
    
    # Find a pair with the same r
    private_key = None
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1, sig2 = sigs[0], sigs[1]
            private_key = recover_private_key(
                r, sig1['s'], sig2['s'], sig1['z'], sig2['z'], n
            )
            break
    
    # Format as 64 lowercase hex characters
    d_hex = format(private_key, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()