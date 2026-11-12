import sys
import json
from typing import List, Tuple

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

def recover_private_key_from_nonce_reuse(
    r: int, s1: int, s2: int, z1: int, z2: int, n: int
) -> int:
    """
    Recover private key when the same nonce k is used for two signatures.
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1 * k - z1) / r mod n
    """
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    signatures = instance['signatures']
    
    # Look for nonce reuse (same r value)
    r_to_sigs = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((i, s, z))
    
    # Find reused nonces
    d = None
    k = None
    
    for r, sigs in r_to_sigs.items():
        if len(sigs) >= 2:
            # Found nonce reuse!
            _, s1, z1 = sigs[0]
            _, s2, z2 = sigs[1]
            
            try:
                d, k = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
                break
            except:
                continue
    
    if d is None:
        raise ValueError("Could not recover private key")
    
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
