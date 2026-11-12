import json
import sys
import base64
from typing import Tuple

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

def recover_private_key(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> int:
    """
    Recover private key from two signatures with the same r value (same k).
    
    ECDSA signature equations:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    From these:
    s1 - s2 = k^(-1) * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    
    Then:
    d = (s*k - z) / r mod n
    """
    # Calculate k from the two signatures
    delta_z = (z1 - z2) % n
    delta_s = (s1 - s2) % n
    
    # k = delta_z / delta_s mod n
    delta_s_inv = mod_inverse(delta_s, n)
    k = (delta_z * delta_s_inv) % n
    
    # Calculate d from k using first signature
    # d = (s1 * k - z1) / r mod n
    r_inv = mod_inverse(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode signatures
    sig1 = instance['signatures'][0]
    sig2 = instance['signatures'][1]
    
    r1 = int.from_bytes(base64.b64decode(sig1['r']), 'big')
    s1 = int.from_bytes(base64.b64decode(sig1['s']), 'big')
    z1 = int.from_bytes(base64.b64decode(sig1['z']), 'big')
    
    r2 = int.from_bytes(base64.b64decode(sig2['r']), 'big')
    s2 = int.from_bytes(base64.b64decode(sig2['s']), 'big')
    z2 = int.from_bytes(base64.b64decode(sig2['z']), 'big')
    
    # Check that r values are the same (nonce reuse attack)
    assert r1 == r2, "r values must be the same for this attack"
    
    # Recover private key
    d = recover_private_key(r1, s1, s2, z1, z2, n)
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
