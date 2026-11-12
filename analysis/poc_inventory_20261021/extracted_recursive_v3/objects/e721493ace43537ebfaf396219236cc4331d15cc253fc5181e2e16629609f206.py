import sys
import json
from typing import List, Tuple

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

def recover_private_key(signatures: List[dict], n: int) -> int:
    """
    Recover private key from ECDSA signatures with nonce reuse.
    If two signatures share the same r value, they used the same nonce k.
    Given: r1 = r2 = r, s1, s2, z1, z2
    We have: s1 = k^-1 * (z1 + r*d) mod n
             s2 = k^-1 * (z2 + r*d) mod n
    Solving: k = (z1 - z2) / (s1 - s2) mod n
             d = (s*k - z) / r mod n
    """
    
    # Group signatures by r value
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append({'r': r, 's': s, 'z': z})
    
    # Find pairs with same r
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1, sig2 = sigs[0], sigs[1]
            
            r_val = sig1['r']
            s1, z1 = sig1['s'], sig1['z']
            s2, z2 = sig2['s'], sig2['z']
            
            # Calculate k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
                
            k = (numerator * mod_inverse(denominator, n)) % n
            
            # Calculate d: d = (s*k - z) / r mod n
            numerator = (s1 * k - z1) % n
            denominator = r_val % n
            
            if denominator == 0:
                continue
                
            d = (numerator * mod_inverse(denominator, n)) % n
            
            if d != 0:
                return d, k
    
    return None, None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Recover private key
    d, k = recover_private_key(signatures, n)
    
    if d is None:
        # Fallback: shouldn't happen with proper nonce reuse
        d = 0
        k = 0
    
    # Format output as 64 lowercase hex characters
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()