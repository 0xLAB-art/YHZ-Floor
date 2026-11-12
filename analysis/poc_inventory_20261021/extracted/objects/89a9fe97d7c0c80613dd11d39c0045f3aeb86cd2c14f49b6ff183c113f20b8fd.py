import json
import sys
import hashlib
from typing import Tuple

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

def bytes_to_int(b: bytes) -> int:
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n: int) -> str:
    """Convert integer to 64-character lowercase hex string."""
    return format(n, '064x')

def recover_private_key(signatures: list, n: int) -> int:
    """
    Recover private key from ECDSA signatures with repeated nonce.
    
    When two signatures share the same r value (meaning same k nonce),
    we can recover k and then the private key d.
    
    From ECDSA: s = k^(-1) * (z + r*d) mod n
    Rearranging: k = (z + r*d) / s mod n
    
    For two signatures with same k:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    Therefore:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    
    # Find signatures with repeated r values
    r_to_sigs = {}
    for sig in signatures:
        r = sig['r']
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append(sig)
    
    # Find a repeated r
    for r_val, sigs in r_to_sigs.items():
        if len(sigs) >= 2:
            sig1, sig2 = sigs[0], sigs[1]
            
            r = sig1['r']
            s1 = sig1['s']
            s2 = sig2['s']
            z1 = sig1['z']
            z2 = sig2['z']
            
            # Calculate k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k = (numerator * modinv(denominator, n)) % n
            
            # Calculate d = (s*k - z) / r mod n
            numerator = (s1 * k - z1) % n
            d = (numerator * modinv(r, n)) % n
            
            return d
    
    raise ValueError("No repeated nonce found")

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse signatures
    import base64
    
    signatures = []
    for sig in instance['signatures']:
        r_bytes = base64.b64decode(sig['r'])
        s_bytes = base64.b64decode(sig['s'])
        z_bytes = base64.b64decode(sig['z'])
        
        signatures.append({
            'r': bytes_to_int(r_bytes),
            's': bytes_to_int(s_bytes),
            'z': bytes_to_int(z_bytes)
        })
    
    # NIST P-256 curve order
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Recover private key
    d = recover_private_key(signatures, n)
    
    # Output result
    result = {"d": int_to_hex(d)}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
