import json
import sys
import base64
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

def bytes_to_int(b: bytes) -> int:
    """Convert bytes to integer (big-endian)."""
    return int.from_bytes(b, 'big')

def int_to_hex(n: int) -> str:
    """Convert integer to 64-character lowercase hex string."""
    hex_str = hex(n)[2:]
    return hex_str.zfill(64)

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode public key
    x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
    y = bytes_to_int(base64.b64decode(instance['public_key']['y']))
    
    # Decode signatures
    sigs = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        sigs.append((r, s, z))
    
    # ECDSA uses secp256k1 curve
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Attack: two signatures with same r value (nonce reuse)
    r1, s1, z1 = sigs[0]
    r2, s2, z2 = sigs[1]
    
    # Since r1 == r2, same k was used
    # s1 = k^-1 * (z1 + r1*d) mod n
    # s2 = k^-1 * (z2 + r2*d) mod n
    # s1 - s2 = k^-1 * (z1 - z2) mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    k = (z_diff * modinv(s_diff, n)) % n
    
    # Now recover private key d
    # s1 = k^-1 * (z1 + r1*d) mod n
    # s1 * k = z1 + r1*d mod n
    # d = (s1*k - z1) / r1 mod n
    
    d = ((s1 * k - z1) * modinv(r1, n)) % n
    
    # Output result
    result = {"d": int_to_hex(d)}
    print(json.dumps(result))

if __name__ == "__main__":
    main()