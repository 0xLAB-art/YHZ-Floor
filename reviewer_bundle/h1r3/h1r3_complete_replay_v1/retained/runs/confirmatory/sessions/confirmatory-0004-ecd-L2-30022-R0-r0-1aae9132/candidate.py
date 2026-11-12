import sys
import json
from typing import Tuple

def modinv(a: int, m: int) -> int:
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def egcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = egcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key_from_nonce_reuse(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> int:
    """
    Recover private key when the same nonce k is used for two signatures.
    
    From ECDSA:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    Therefore:
    s1 - s2 = k^-1 * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    
    Then:
    d = (s*k - z) / r mod n
    """
    # Calculate k
    k = ((z1 - z2) * modinv(s1 - s2, n)) % n
    
    # Calculate private key d
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA uses secp256k1 curve
    # Order of the curve
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Convert hex strings to integers
    sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sigs.append((r, s, z))
    
    # Look for signatures with the same r value (indicating nonce reuse)
    r_to_sigs = {}
    for i, (r, s, z) in enumerate(sigs):
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((i, s, z))
    
    # Find a pair with the same r
    d = None
    for r, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            # We found nonce reuse!
            _, s1, z1 = sig_list[0]
            _, s2, z2 = sig_list[1]
            
            try:
                d = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
                break
            except:
                continue
    
    if d is None:
        # Fallback: try other cryptographic attacks or analysis
        # For this problem, nonce reuse should be the vulnerability
        d = 0
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
