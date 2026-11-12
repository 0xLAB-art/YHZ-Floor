import json
import sys
import hashlib
from typing import Tuple

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

def bytes_to_int(b: bytes) -> int:
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n: int) -> str:
    """Convert integer to 64-character lowercase hex string."""
    hex_str = hex(n)[2:]
    if hex_str.endswith('L'):
        hex_str = hex_str[:-1]
    return hex_str.zfill(64)

def main():
    import base64
    
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
    y = bytes_to_int(base64.b64decode(instance['public_key']['y']))
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # ECDSA uses secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Look for duplicate r values (nonce reuse attack)
    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            r1, s1, z1 = signatures[i]
            r2, s2, z2 = signatures[j]
            
            if r1 == r2:
                # Same nonce k used for two signatures
                # k = (z1 - z2) / (s1 - s2) mod n
                # d = (s1*k - z1) / r1 mod n
                
                s_diff = (s1 - s2) % n
                z_diff = (z1 - z2) % n
                
                try:
                    s_diff_inv = modinv(s_diff, n)
                    k = (z_diff * s_diff_inv) % n
                    
                    # Calculate private key d
                    r_inv = modinv(r1, n)
                    d = ((s1 * k - z1) * r_inv) % n
                    
                    # Output result
                    result = {"d": int_to_hex(d)}
                    print(json.dumps(result))
                    return
                except ValueError:
                    continue
    
    # If no duplicate r found, should not happen for valid instance
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()