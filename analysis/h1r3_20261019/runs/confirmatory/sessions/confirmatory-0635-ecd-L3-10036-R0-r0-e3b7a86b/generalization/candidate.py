import sys
import json
from typing import List, Tuple

def modinv(a: int, m: int) -> int:
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean algorithm. Returns (gcd, x, y) where gcd = ax + by."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(sig1: dict, sig2: dict, n: int) -> int:
    """Recover private key from two signatures with the same r value (nonce reuse)."""
    r = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    s2 = int(sig2['s'], 16)
    z1 = int(sig1['z'], 16)
    z2 = int(sig2['z'], 16)
    
    # From ECDSA: s = k^(-1) * (z + r*d) mod n
    # s1 = k^(-1) * (z1 + r*d) mod n
    # s2 = k^(-1) * (z2 + r*d) mod n
    # s1 - s2 = k^(-1) * (z1 - z2) mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    # k = z_diff / s_diff mod n
    k = (z_diff * modinv(s_diff, n)) % n
    
    # Now recover d from: s1 = k^(-1) * (z1 + r*d) mod n
    # s1 * k = z1 + r*d mod n
    # d = (s1*k - z1) / r mod n
    
    k_inv = modinv(k, n)
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find signatures with the same r value (nonce reuse vulnerability)
    r_groups = {}
    for sig in signatures:
        r = sig['r']
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(sig)
    
    # Find a group with at least 2 signatures (nonce reuse)
    d = None
    k = None
    
    for r_val, sigs in r_groups.items():
        if len(sigs) >= 2:
            # We found nonce reuse! Recover the private key
            try:
                d, k = recover_private_key(sigs[0], sigs[1], n)
                break
            except:
                continue
    
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
