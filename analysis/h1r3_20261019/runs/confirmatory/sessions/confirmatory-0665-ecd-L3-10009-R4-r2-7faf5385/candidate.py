import sys
import json
from typing import Optional

def modinv(a: int, m: int) -> int:
    """Compute modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a: int, b: int) -> tuple:
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key_from_nonce_reuse(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> Optional[int]:
    """Recover private key when same nonce k is used for two signatures."""
    # k = (z1 - z2) / (s1 - s2) mod n
    # d = (s*k - z) / r mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    try:
        s_diff_inv = modinv(s_diff, n)
    except ValueError:
        return None
    
    k = (z_diff * s_diff_inv) % n
    
    # Now compute d from the first signature
    try:
        r_inv = modinv(r, n)
    except ValueError:
        return None
    
    d = (((s1 * k - z1) % n) * r_inv) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # ECDSA curve parameters (secp256k1)
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Look for nonce reuse: same r value in different signatures
    r_to_sigs = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((i, s, z))
    
    # Find r values that appear more than once
    d = None
    k = None
    
    for r, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            # We found nonce reuse!
            idx1, s1, z1 = sig_list[0]
            idx2, s2, z2 = sig_list[1]
            
            result = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
            if result:
                d, k = result
                break
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    output = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(output))

if __name__ == "__main__":
    main()
