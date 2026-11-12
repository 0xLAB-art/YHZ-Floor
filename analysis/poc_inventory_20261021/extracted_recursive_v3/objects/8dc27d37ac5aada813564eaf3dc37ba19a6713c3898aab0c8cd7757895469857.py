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

def recover_private_key(sigs: List[dict]) -> str:
    """
    Recover ECDSA private key from signatures with repeated nonces.
    
    If two signatures share the same r value, they used the same k (nonce).
    For ECDSA: s = k^(-1) * (z + r*d) mod n
    
    With same k for two messages:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    Therefore:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    # secp256k1 order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Group signatures by r value
    r_groups = {}
    for sig in sigs:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append((s, z))
    
    # Find r values that appear more than once (nonce reuse)
    for r, sig_list in r_groups.items():
        if len(sig_list) >= 2:
            # Use first two signatures with this r
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            # Calculate k: k = (z1 - z2) * (s1 - s2)^(-1) mod n
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            try:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Calculate d: d = (s*k - z) * r^(-1) mod n
                r_inv = modinv(r, n)
                d = ((s1 * k - z1) * r_inv) % n
                
                # Verify with second signature
                d_check = ((s2 * k - z2) * r_inv) % n
                
                if d == d_check and d > 0:
                    return format(d, '064x')
            except ValueError:
                continue
    
    raise ValueError("Could not recover private key")

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # Recover private key
    d = recover_private_key(signatures)
    
    # Output result
    result = {"d": d}
    print(json.dumps(result))

if __name__ == "__main__":
    main()