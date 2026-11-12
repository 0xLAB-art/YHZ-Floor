import json
import sys
from typing import List, Tuple

def modinv(a: int, m: int) -> int:
    """Compute modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(signatures: List[dict], n: int) -> int:
    """
    Recover private key from ECDSA signatures with repeated nonce (k).
    
    When two signatures share the same r value, they used the same k.
    Given: s1 = k^(-1) * (z1 + r*d) mod n
           s2 = k^(-1) * (z2 + r*d) mod n
    
    We can solve for k and then d.
    """
    # Find signatures with the same r value
    r_to_sigs = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((s, z))
    
    # Find a pair with duplicate r
    for r, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            # From the two equations:
            # s1 = k^(-1) * (z1 + r*d) mod n
            # s2 = k^(-1) * (z2 + r*d) mod n
            #
            # Multiply by k:
            # k*s1 = z1 + r*d mod n
            # k*s2 = z2 + r*d mod n
            #
            # Subtract:
            # k*(s1 - s2) = z1 - z2 mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
            
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Now recover d from: s1 = k^(-1) * (z1 + r*d) mod n
            # k*s1 = z1 + r*d mod n
            # r*d = k*s1 - z1 mod n
            # d = (k*s1 - z1) / r mod n
            
            k_s1 = (k * s1) % n
            numerator = (k_s1 - z1) % n
            
            if r == 0:
                continue
            
            d = (numerator * modinv(r, n)) % n
            
            return d, k
    
    raise ValueError("No duplicate r values found")

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256K1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Recover private key
    d, k = recover_private_key(signatures, n)
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
