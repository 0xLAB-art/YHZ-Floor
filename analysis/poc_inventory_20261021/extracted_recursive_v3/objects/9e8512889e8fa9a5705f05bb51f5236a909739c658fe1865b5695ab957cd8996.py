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

def recover_private_key_from_nonce_reuse(
    r: int, s1: int, s2: int, z1: int, z2: int, n: int
) -> int:
    """
    Recover private key when the same nonce k is used for two signatures.
    
    From ECDSA equations:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    Solving for k:
    k = (z1 - z2) / (s1 - s2) mod n
    
    Then solving for d:
    d = (s*k - z) / r mod n
    """
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    r_inv = modinv(r, n)
    d = (r_inv * (s1 * k - z1)) % n
    
    return d, k

def main():
    if len(sys.argv) != 2:
        return
    
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Look for duplicate r values (indicating nonce reuse)
    r_to_sigs: Dict[str, List[int]] = {}
    
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append(i)
    
    # Find a pair with the same r value
    for r_hex, indices in r_to_sigs.items():
        if len(indices) >= 2:
            i1, i2 = indices[0], indices[1]
            sig1 = signatures[i1]
            sig2 = signatures[i2]
            
            r = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            d, k = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
            
            # Format output
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            
            print(json.dumps(result))
            return
    
    # If no duplicates found, return empty (shouldn't happen for valid challenge)
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()