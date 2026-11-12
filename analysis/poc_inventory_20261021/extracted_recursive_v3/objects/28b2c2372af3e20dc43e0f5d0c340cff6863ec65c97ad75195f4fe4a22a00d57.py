import json
import sys
import hashlib
from typing import List, Tuple
import base64

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

def bytes_to_int(b: bytes) -> int:
    """Convert bytes to integer."""
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
    pub_x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
    pub_y = bytes_to_int(base64.b64decode(instance['public_key']['y']))
    
    # Decode signatures
    signatures = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # SECP256k1 curve parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Look for signature pairs with the same r value (nonce reuse)
    # If k is reused: k = (z1 - z2) / (s1 - s2) mod n
    # Then: d = (s * k - z) / r mod n
    
    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            r1, s1, z1 = signatures[i]
            r2, s2, z2 = signatures[j]
            
            if r1 == r2:
                # Nonce reuse detected!
                # k = (z1 - z2) * (s1 - s2)^(-1) mod n
                s_diff = (s1 - s2) % n
                z_diff = (z1 - z2) % n
                
                try:
                    s_diff_inv = modinv(s_diff, n)
                    k = (z_diff * s_diff_inv) % n
                    
                    # Recover private key: d = (s * k - z) / r mod n
                    r_inv = modinv(r1, n)
                    d = ((s1 * k - z1) * r_inv) % n
                    
                    # Output result
                    result = {"d": int_to_hex(d)}
                    print(json.dumps(result))
                    return
                except ValueError:
                    continue
    
    # If no nonce reuse found, output a placeholder
    result = {"d": "0" * 64}
    print(json.dumps(result))

if __name__ == "__main__":
    main()