import sys
import json
from typing import Tuple, Optional

def mod_inverse(a: int, m: int) -> int:
    """Compute modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def recover_k_from_repeated_r(r: int, s1: int, z1: int, s2: int, z2: int, n: int) -> Optional[int]:
    """Recover nonce k when the same r is used in two signatures."""
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    try:
        s_diff_inv = mod_inverse(s_diff, n)
        k = (z_diff * s_diff_inv) % n
        return k
    except ValueError:
        return None

def recover_private_key(k: int, r: int, s: int, z: int, n: int) -> int:
    """Recover private key d from known k."""
    try:
        r_inv = mod_inverse(r, n)
        d = (r_inv * (s * k - z)) % n
        return d
    except ValueError:
        return None

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Build a map of r values to their signatures
    r_to_sigs = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((s, z))
    
    # Find repeated r values
    d = None
    k = None
    
    for r, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            # We have at least two signatures with the same r
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            # Try to recover k
            k_recovered = recover_k_from_repeated_r(r, s1, z1, s2, z2, n)
            
            if k_recovered is not None:
                # Recover private key d
                d_recovered = recover_private_key(k_recovered, r, s1, z1, n)
                
                if d_recovered is not None:
                    d = d_recovered
                    k = k_recovered
                    break
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()