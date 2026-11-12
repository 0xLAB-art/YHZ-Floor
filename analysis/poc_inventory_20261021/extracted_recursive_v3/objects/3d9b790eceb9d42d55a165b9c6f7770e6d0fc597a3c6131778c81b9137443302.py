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

def recover_private_key(n: int, sig1: Dict, sig2: Dict) -> int:
    """
    Recover private key from two ECDSA signatures that share the same k (nonce).
    
    ECDSA signature equation: s = k^(-1) * (z + r*d) mod n
    Rearranging: k = (z + r*d) / s mod n
    
    For two signatures with same k:
    k = (z1 + r1*d) / s1 = (z2 + r2*d) / s2 mod n
    
    Cross multiply and solve for d:
    s2*(z1 + r1*d) = s1*(z2 + r2*d) mod n
    s2*z1 + s2*r1*d = s1*z2 + s1*r2*d mod n
    s2*z1 - s1*z2 = d*(s1*r2 - s2*r1) mod n
    d = (s2*z1 - s1*z2) / (s1*r2 - s2*r1) mod n
    """
    r1 = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    
    r2 = int(sig2['r'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Calculate numerator and denominator
    numerator = (s2 * z1 - s1 * z2) % n
    denominator = (s1 * r2 - s2 * r1) % n
    
    if denominator == 0:
        return None
    
    # d = numerator / denominator mod n
    d = (numerator * modinv(denominator, n)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find signatures with the same r value (indicating same k nonce)
    r_groups = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(i)
    
    # Find a pair with same r
    private_key = None
    for r, indices in r_groups.items():
        if len(indices) >= 2:
            # Try to recover private key from this pair
            sig1 = signatures[indices[0]]
            sig2 = signatures[indices[1]]
            
            d = recover_private_key(n, sig1, sig2)
            if d is not None:
                private_key = d
                break
    
    # Format output
    if private_key is not None:
        d_hex = format(private_key, '064x')
    else:
        d_hex = '0' * 64
    
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()