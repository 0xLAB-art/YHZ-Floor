import sys
import json
import base64
import hashlib
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

def bytes_to_int(b: bytes) -> int:
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n: int) -> str:
    """Convert integer to 64-character lowercase hex string."""
    return format(n, '064x')

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # Parse public key
    x_bytes = base64.b64decode(data['public_key']['x'])
    y_bytes = base64.b64decode(data['public_key']['y'])
    
    # Parse signatures
    signatures = []
    for sig in data['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find two signatures with the same r value (nonce reuse)
    r_to_sigs = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_to_sigs:
            # Found nonce reuse!
            j = r_to_sigs[r]
            r1, s1, z1 = signatures[j]
            r2, s2, z2 = signatures[i]
            
            # Recover k (nonce) and d (private key)
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s*k - z) / r mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Calculate d using the first signature
            r_inv = modinv(r1, n)
            d = ((s1 * k - z1) * r_inv) % n
            
            # Output result
            result = {
                "d": int_to_hex(d),
                "k": int_to_hex(k)
            }
            print(json.dumps(result))
            return
        else:
            r_to_sigs[r] = i
    
    # Should not reach here if there's nonce reuse
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()
