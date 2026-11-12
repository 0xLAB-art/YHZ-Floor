import sys
import json
from typing import Dict, List, Tuple

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

def recover_private_key_from_nonce_reuse(
    r: int, s1: int, s2: int, z1: int, z2: int, n: int
) -> int:
    """Recover private key k when nonce is reused."""
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None
    
    k = (numerator * mod_inverse(denominator, n)) % n
    return k

def recover_private_key_d(k: int, r: int, s: int, z: int, n: int) -> int:
    """Recover private key d from known nonce k."""
    # s = k^(-1) * (z + r*d) mod n
    # s*k = z + r*d mod n
    # r*d = s*k - z mod n
    # d = (s*k - z) / r mod n
    
    numerator = (s * k - z) % n
    d = (numerator * mod_inverse(r, n)) % n
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA parameters for secp256k1
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Parse signatures
    sig_data = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sig_data.append((r, s, z))
    
    # Look for nonce reuse (same r value)
    r_dict: Dict[int, List[Tuple[int, int, int]]] = {}
    for i, (r, s, z) in enumerate(sig_data):
        if r not in r_dict:
            r_dict[r] = []
        r_dict[r].append((i, s, z))
    
    # Find nonce reuse
    k = None
    d = None
    
    for r, occurrences in r_dict.items():
        if len(occurrences) >= 2:
            # Nonce reuse found
            idx1, s1, z1 = occurrences[0]
            idx2, s2, z2 = occurrences[1]
            
            k = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
            if k is not None and k != 0:
                # Recover private key d
                d = recover_private_key_d(k, r, s1, z1, n)
                break
    
    # Format output
    if d is None or k is None:
        # Fallback - shouldn't happen with valid nonce reuse
        d = 0
        k = 0
    
    result = {
        "d": format(d, '064x'),
        "k": format(k, '064x')
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()