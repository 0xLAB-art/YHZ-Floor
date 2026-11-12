import sys
import json
import base64
from typing import List, Tuple

def mod_inverse(a: int, m: int) -> int:
    """Extended Euclidean algorithm for modular inverse"""
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

def bytes_to_int(b: bytes) -> int:
    """Convert bytes to integer"""
    return int.from_bytes(b, 'big')

def int_to_hex(n: int) -> str:
    """Convert integer to 64-character hex string"""
    return format(n, '064x')

def recover_private_key(signatures: List[dict], n: int) -> Tuple[int, int]:
    """
    Recover private key using repeated nonce attack.
    If two signatures use the same r value (same k), we can recover k and then d.
    
    For ECDSA:
    s1 = (z1 + r*d) * k^(-1) mod n
    s2 = (z2 + r*d) * k^(-1) mod n
    
    From these:
    s1 - s2 = (z1 - z2) * k^(-1) mod n
    k = (z1 - z2) * (s1 - s2)^(-1) mod n
    d = (s*k - z) * r^(-1) mod n
    """
    
    # Group signatures by r value
    r_groups = {}
    for sig in signatures:
        r = sig['r']
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(sig)
    
    # Find r values that appear more than once
    for r_b64, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1, sig2 = sigs[0], sigs[1]
            
            r = bytes_to_int(base64.b64decode(sig1['r']))
            s1 = bytes_to_int(base64.b64decode(sig1['s']))
            s2 = bytes_to_int(base64.b64decode(sig2['s']))
            z1 = bytes_to_int(base64.b64decode(sig1['z']))
            z2 = bytes_to_int(base64.b64decode(sig2['z']))
            
            # Calculate k
            z_diff = (z1 - z2) % n
            s_diff = (s1 - s2) % n
            
            try:
                s_diff_inv = mod_inverse(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Calculate d using first signature
                k_inv = mod_inverse(k, n)
                r_inv = mod_inverse(r, n)
                d = ((s1 * k - z1) * r_inv) % n
                
                return d, k
            except ValueError:
                continue
    
    raise ValueError("Could not recover private key")

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Recover private key
    d, k = recover_private_key(instance['signatures'], n)
    
    # Output result
    result = {
        "d": int_to_hex(d),
        "k": int_to_hex(k)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()