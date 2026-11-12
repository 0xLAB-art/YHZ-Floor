import sys
import json
from typing import Tuple, Optional

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

def recover_private_key_from_nonce_reuse(
    r: int, s1: int, s2: int, z1: int, z2: int, n: int
) -> Optional[int]:
    """
    Recover private key from two signatures that use the same nonce k.
    
    For ECDSA:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    From these we can derive:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    try:
        s_diff_inv = modinv(s_diff, n)
    except ValueError:
        return None
    
    k = (z_diff * s_diff_inv) % n
    
    try:
        r_inv = modinv(r, n)
    except ValueError:
        return None
    
    d = (r_inv * (s1 * k - z1)) % n
    
    return d

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    pub_x = int(instance['public_key']['x'], 16)
    pub_y = int(instance['public_key']['y'], 16)
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # Look for signatures with the same r value (nonce reuse)
    r_groups = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append((i, s, z))
    
    # Find a pair with the same r
    private_key = None
    nonce = None
    
    for r, group in r_groups.items():
        if len(group) >= 2:
            # We have nonce reuse!
            idx1, s1, z1 = group[0]
            idx2, s2, z2 = group[1]
            
            # Recover private key
            d = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
            
            if d is not None:
                # Recover nonce k from first signature
                try:
                    r_inv = modinv(r, n)
                    k = ((s1 * d - z1) * modinv(s1, n)) % n
                    # Alternative: k = (z1 + r*d) * modinv(s1, n) % n
                    s1_inv = modinv(s1, n)
                    k = ((z1 + r * d) * s1_inv) % n
                    
                    private_key = d
                    nonce = k
                    break
                except ValueError:
                    continue
    
    if private_key is None:
        # Fallback: try all pairs
        for i in range(len(signatures)):
            for j in range(i + 1, len(signatures)):
                r1, s1, z1 = signatures[i]
                r2, s2, z2 = signatures[j]
                
                if r1 == r2:
                    d = recover_private_key_from_nonce_reuse(r1, s1, s2, z1, z2, n)
                    if d is not None:
                        try:
                            s1_inv = modinv(s1, n)
                            k = ((z1 + r1 * d) * s1_inv) % n
                            private_key = d
                            nonce = k
                            break
                        except ValueError:
                            continue
            if private_key is not None:
                break
    
    # Format output
    d_hex = format(private_key, '064x')
    k_hex = format(nonce, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()