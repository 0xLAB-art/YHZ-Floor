import json
import sys
from typing import List, Tuple
from math import gcd

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    gcd_val, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd_val, x, y

def mod_inverse(a: int, m: int) -> int:
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Look for signature pairs with the same r value
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find pairs with same r
    for r_val, indices in r_map.items():
        if len(indices) >= 2:
            # We have at least two signatures with the same r
            i, j = indices[0], indices[1]
            sig1 = signatures[i]
            sig2 = signatures[j]
            
            r = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # From ECDSA: s = k^-1(z + rd) mod n
            # s1 = k^-1(z1 + rd) mod n
            # s2 = k^-1(z2 + rd) mod n
            # Therefore: s1 - s2 = k^-1(z1 - z2) mod n
            # So: k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
            
            try:
                s_diff_inv = mod_inverse(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Now recover d from: s1 = k^-1(z1 + rd) mod n
                # So: s1 * k = z1 + rd mod n
                # Therefore: d = (s1 * k - z1) / r mod n
                
                k_inv = mod_inverse(k, n)
                r_inv = mod_inverse(r, n)
                d = ((s1 * k - z1) * r_inv) % n
                
                # Format as 64 hex characters
                d_hex = format(d, '064x')
                
                result = {"d": d_hex}
                print(json.dumps(result))
                return
            except ValueError:
                continue
    
    # If no same r found, shouldn't happen based on the instance
    result = {"d": "0" * 64}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
