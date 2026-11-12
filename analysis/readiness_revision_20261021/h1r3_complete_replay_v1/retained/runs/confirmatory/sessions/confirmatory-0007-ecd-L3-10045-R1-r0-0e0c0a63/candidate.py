import sys
import json
from typing import Dict, List, Tuple

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

def recover_private_key_from_reused_nonce(
    r1: int, s1: int, z1: int,
    r2: int, s2: int, z2: int,
    n: int
) -> int:
    """
    Recover private key when the same nonce k is used for two signatures.
    
    From ECDSA equations:
    s1 = k^(-1) * (z1 + r1 * d) mod n
    s2 = k^(-1) * (z2 + r2 * d) mod n
    
    If r1 == r2, then the same k was used.
    We can solve: k = (z1 - z2) / (s1 - s2) mod n
    Then: d = (s1 * k - z1) / r1 mod n
    """
    if r1 != r2:
        return None
    
    # Calculate k = (z1 - z2) * (s1 - s2)^(-1) mod n
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    if s_diff == 0:
        return None
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d = (s1 * k - z1) * r1^(-1) mod n
    r_inv = modinv(r1, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Convert signatures to integers
    sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sigs.append((r, s, z))
    
    # Look for repeated r values (nonce reuse)
    d = None
    for i in range(len(sigs)):
        for j in range(i + 1, len(sigs)):
            r1, s1, z1 = sigs[i]
            r2, s2, z2 = sigs[j]
            
            if r1 == r2:
                # Found nonce reuse!
                d = recover_private_key_from_reused_nonce(r1, s1, z1, r2, s2, z2, n)
                if d is not None:
                    # Also recover k for completeness
                    s_diff = (s1 - s2) % n
                    z_diff = (z1 - z2) % n
                    s_diff_inv = modinv(s_diff, n)
                    k = (z_diff * s_diff_inv) % n
                    
                    # Format as 64 lowercase hex characters
                    d_hex = format(d, '064x')
                    k_hex = format(k, '064x')
                    
                    result = {
                        "d": d_hex,
                        "k": k_hex
                    }
                    print(json.dumps(result))
                    return
    
    # Should not reach here if instance is valid
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()
