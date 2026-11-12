import sys
import json
from typing import Optional, Tuple

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
) -> Optional[int]:
    """
    Recover private key when the same nonce k is used for two signatures.
    
    From ECDSA:
    s1 = k^(-1) * (z1 + r * d) mod n
    s2 = k^(-1) * (z2 + r * d) mod n
    
    Therefore:
    s1 - s2 = k^(-1) * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1 * k - z1) / r mod n
    """
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    if s_diff == 0:
        return None
    
    try:
        s_diff_inv = modinv(s_diff, n)
        k = (z_diff * s_diff_inv) % n
        
        # Recover private key d
        r_inv = modinv(r, n)
        d = ((s1 * k - z1) * r_inv) % n
        
        return d
    except ValueError:
        return None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # NIST P-256 curve order
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    signatures = instance['signatures']
    
    # Parse signatures
    parsed_sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        parsed_sigs.append((r, s, z))
    
    # Look for repeated r values (nonce reuse)
    r_to_indices = {}
    for i, (r, s, z) in enumerate(parsed_sigs):
        if r not in r_to_indices:
            r_to_indices[r] = []
        r_to_indices[r].append(i)
    
    # Find nonce reuse
    d = None
    k = None
    
    for r, indices in r_to_indices.items():
        if len(indices) >= 2:
            # Found nonce reuse
            i1, i2 = indices[0], indices[1]
            r1, s1, z1 = parsed_sigs[i1]
            r2, s2, z2 = parsed_sigs[i2]
            
            # Recover private key
            d_candidate = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
            
            if d_candidate is not None:
                d = d_candidate
                # Recover k from first signature
                try:
                    r_inv = modinv(r, n)
                    k = ((s1 * d_candidate - z1) * modinv(s1, n)) % n
                    # Alternative: k = (z1 + r * d) * modinv(s1, n) % n
                    k = ((z1 + r * d_candidate) * modinv(s1, n)) % n
                except ValueError:
                    pass
                break
    
    # Format output
    if d is not None and k is not None:
        d_hex = format(d, '064x')
        k_hex = format(k, '064x')
    else:
        d_hex = '0' * 64
        k_hex = '0' * 64
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
