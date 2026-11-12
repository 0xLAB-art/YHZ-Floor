import sys
import json
from typing import Dict, List, Tuple

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

def recover_private_key(signatures: List[Dict[str, str]], n: int) -> int:
    """
    Recover private key from ECDSA signatures with nonce reuse.
    If two signatures share the same r value, they used the same nonce k.
    From two such signatures, we can recover k and then the private key d.
    """
    # Group signatures by r value
    r_groups: Dict[str, List[Dict[str, int]]] = {}
    
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        r_hex = sig['r']
        if r_hex not in r_groups:
            r_groups[r_hex] = []
        r_groups[r_hex].append({'r': r, 's': s, 'z': z})
    
    # Find signatures with same r (nonce reuse)
    for r_hex, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1, sig2 = sigs[0], sigs[1]
            r = sig1['r']
            s1, z1 = sig1['s'], sig1['z']
            s2, z2 = sig2['s'], sig2['z']
            
            # From ECDSA: s = k^(-1) * (z + r*d) mod n
            # s1 = k^(-1) * (z1 + r*d) mod n
            # s2 = k^(-1) * (z2 + r*d) mod n
            # Therefore: s1 - s2 = k^(-1) * (z1 - z2) mod n
            # So: k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
            
            try:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Now recover private key d from: s1 = k^(-1) * (z1 + r*d) mod n
                # k * s1 = z1 + r*d mod n
                # d = (k * s1 - z1) / r mod n
                
                if r == 0:
                    continue
                
                r_inv = modinv(r, n)
                d = ((k * s1 - z1) % n * r_inv) % n
                
                return d, k
            except ValueError:
                continue
    
    raise ValueError("Could not recover private key")

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Recover private key and nonce
    d, k = recover_private_key(signatures, n)
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    # Output result
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
