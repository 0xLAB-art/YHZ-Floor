import sys
import json
from collections import defaultdict

def mod_inverse(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n):
    """
    Recover private key k (nonce) when the same nonce is used twice.
    k = (z1 - z2) / (s1 - s2) mod n
    Then recover d = (s*k - z) / r mod n
    """
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    try:
        s_diff_inv = mod_inverse(s_diff, n)
        k = (z_diff * s_diff_inv) % n
        
        # Now recover d using: d = (s*k - z) / r mod n
        r_inv = mod_inverse(r, n)
        d = ((s1 * k - z1) * r_inv) % n
        
        return d
    except ValueError:
        return None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Group signatures by r value (nonce reuse)
    r_groups = defaultdict(list)
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        r_groups[r].append((s, z))
    
    # Find r values that appear multiple times (nonce reuse)
    d = None
    for r, sig_list in r_groups.items():
        if len(sig_list) >= 2:
            # We have nonce reuse!
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            d = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
            if d is not None:
                break
    
    if d is None:
        # Fallback: should not happen with nonce reuse present
        d = 0
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()