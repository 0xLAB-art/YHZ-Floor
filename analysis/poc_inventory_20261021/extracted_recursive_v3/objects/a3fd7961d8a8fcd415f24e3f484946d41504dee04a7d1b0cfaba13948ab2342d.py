import sys
import json
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

def recover_private_key(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> int:
    """
    Recover private key from two signatures with the same nonce (r value).
    
    From ECDSA equations:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    Solving for k:
    s1 - s2 = k^-1 * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    
    Then solving for d:
    d = (s*k - z) / r mod n
    """
    # Calculate k (the nonce)
    delta_z = (z1 - z2) % n
    delta_s = (s1 - s2) % n
    
    if delta_s == 0:
        return None
    
    k = (delta_z * modinv(delta_s, n)) % n
    
    # Calculate private key d using first signature
    d = (modinv(r, n) * (s1 * k - z1)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256K1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find signatures with the same r value (nonce reuse)
    r_groups = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(i)
    
    # Find a pair with the same r
    for r, indices in r_groups.items():
        if len(indices) >= 2:
            # Use first two signatures with same r
            idx1, idx2 = indices[0], indices[1]
            sig1 = signatures[idx1]
            sig2 = signatures[idx2]
            
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            d = recover_private_key(r, s1, s2, z1, z2, n)
            
            if d is not None:
                # Format as 64 lowercase hex characters
                d_hex = format(d, '064x')
                result = {"d": d_hex}
                print(json.dumps(result))
                return
    
    # Should not reach here if instance is valid
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()