import sys
import json
from typing import Dict

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

def recover_private_key(r: int, s1: int, z1: int, s2: int, z2: int, n: int) -> tuple:
    """Recover private key d and nonce k from two signatures with same r."""
    # k = (z1 - z2) / (s1 - s2) mod n
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # d = (s*k - z) / r mod n
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find signatures with same r value
    r_map: Dict[str, list] = {}
    for sig in signatures:
        r = sig['r']
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(sig)
    
    # Find a pair with same r
    for r_hex, sigs in r_map.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1, sig2 = sigs[0], sigs[1]
            
            r = int(r_hex, 16)
            s1 = int(sig1['s'], 16)
            z1 = int(sig1['z'], 16)
            s2 = int(sig2['s'], 16)
            z2 = int(sig2['z'], 16)
            
            # Recover private key
            d, k = recover_private_key(r, s1, z1, s2, z2, n)
            
            # Format as 64 character lowercase hex
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {"d": d_hex, "k": k_hex}
            print(json.dumps(result))
            return
    
    # If no repeated r found, something is wrong
    raise ValueError("No repeated r values found")

if __name__ == "__main__":
    main()