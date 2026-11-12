import json
import sys
from typing import Tuple

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

def base64_to_int(b64_str: str) -> int:
    """Convert base64 string to integer."""
    import base64
    byte_data = base64.b64decode(b64_str)
    return int.from_bytes(byte_data, byteorder='big')

def recover_private_key(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> int:
    """
    Recover private key from two signatures with the same r value (nonce reuse).
    
    Given:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    We can solve:
    s1 - s2 = k^-1 * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1*k - z1) / r mod n
    """
    # Calculate k from the difference
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    # k = z_diff / s_diff mod n
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d from k
    # s1 = k^-1 * (z1 + r*d) mod n
    # s1 * k = z1 + r*d mod n
    # d = (s1*k - z1) / r mod n
    k_inv = modinv(k, n)
    
    # Verify which signature equation to use
    numerator = (s1 * k - z1) % n
    r_inv = modinv(r, n)
    d = (numerator * r_inv) % n
    
    return d

def main():
    # NIST P-256 curve parameters
    p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
    n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
    
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    x = base64_to_int(instance['public_key']['x'])
    y = base64_to_int(instance['public_key']['y'])
    
    # Parse signatures
    sig1 = instance['signatures'][0]
    sig2 = instance['signatures'][1]
    
    r1 = base64_to_int(sig1['r'])
    s1 = base64_to_int(sig1['s'])
    z1 = base64_to_int(sig1['z'])
    
    r2 = base64_to_int(sig2['r'])
    s2 = base64_to_int(sig2['s'])
    z2 = base64_to_int(sig2['z'])
    
    # Check if r values are the same (nonce reuse attack)
    if r1 == r2:
        d = recover_private_key(r1, s1, s2, z1, z2, n)
        
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        
        result = {"d": d_hex}
        print(json.dumps(result))
    else:
        # Different attack needed
        raise ValueError("r values are different, cannot apply nonce reuse attack")

if __name__ == "__main__":
    main()
