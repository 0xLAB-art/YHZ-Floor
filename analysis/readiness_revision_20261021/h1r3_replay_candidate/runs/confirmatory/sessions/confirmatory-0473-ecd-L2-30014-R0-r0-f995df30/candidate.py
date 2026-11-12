import sys
import json
from typing import Tuple, Optional

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
) -> Optional[int]:
    """
    Recover private key when the same nonce k is used for two signatures.
    
    For ECDSA signatures with the same r value (same k):
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    From these we can derive:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    # Calculate k from the two signatures
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    try:
        s_diff_inv = modinv(s_diff, n)
    except ValueError:
        return None
    
    k = (z_diff * s_diff_inv) % n
    
    # Calculate private key d from k
    try:
        r_inv = modinv(r, n)
    except ValueError:
        return None
    
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # Look for signatures with the same r value (nonce reuse)
    r_groups = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append((i, s, z))
    
    # Find a group with at least 2 signatures (nonce reuse)
    private_key = None
    for r, group in r_groups.items():
        if len(group) >= 2:
            # Use first two signatures with same r
            _, s1, z1 = group[0]
            _, s2, z2 = group[1]
            
            private_key = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
            if private_key is not None:
                break
    
    if private_key is None:
        # Fallback (shouldn't happen with the given instance)
        private_key = 0
    
    # Format as 64 lowercase hex characters
    d_hex = format(private_key, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
