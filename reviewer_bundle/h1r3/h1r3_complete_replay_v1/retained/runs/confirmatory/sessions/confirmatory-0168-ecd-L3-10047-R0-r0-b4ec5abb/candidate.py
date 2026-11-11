import sys
import json
from typing import Dict, List, Tuple
from collections import defaultdict

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

def attack_ecdsa_nonce_reuse(signatures: List[Dict[str, str]], n: int) -> int:
    """
    Recover private key from ECDSA signatures with nonce reuse.
    If r values match, the same k was used, allowing private key recovery.
    """
    # Group signatures by r value
    r_groups = defaultdict(list)
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        r_groups[r].append((s, z))
    
    # Find r values with multiple signatures
    for r, sig_list in r_groups.items():
        if len(sig_list) >= 2:
            # Use first two signatures with same r
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            # From ECDSA equations:
            # s1 = k^-1 * (z1 + r*d) mod n
            # s2 = k^-1 * (z2 + r*d) mod n
            # 
            # Therefore:
            # s1 - s2 = k^-1 * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
            
            try:
                s_diff_inv = mod_inverse(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Recover private key d from: s1 = k^-1 * (z1 + r*d) mod n
                # Therefore: d = (s1*k - z1) / r mod n
                k_inv = mod_inverse(k, n)
                
                # Verify k_inv is correct
                if (k * k_inv) % n != 1:
                    continue
                
                r_inv = mod_inverse(r, n)
                d = ((s1 * k - z1) * r_inv) % n
                
                return d, k
            except ValueError:
                continue
    
    return None, None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Attempt nonce reuse attack
    d, k = attack_ecdsa_nonce_reuse(signatures, n)
    
    if d is not None and k is not None:
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        k_hex = format(k, '064x')
        
        result = {
            "d": d_hex,
            "k": k_hex
        }
        
        print(json.dumps(result))
    else:
        # Should not happen with valid input
        print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()
