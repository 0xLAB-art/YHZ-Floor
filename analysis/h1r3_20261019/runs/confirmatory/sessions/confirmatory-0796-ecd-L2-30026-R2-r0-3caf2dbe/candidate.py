import sys
import json
import base64
from typing import List, Tuple

def modinv(a: int, m: int) -> int:
    """Compute modular inverse using extended Euclidean algorithm."""
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

def bytes_to_int(b: bytes) -> int:
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n: int) -> str:
    """Convert integer to 64-character hex string."""
    return format(n, '064x')

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode public key
    x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
    y = bytes_to_int(base64.b64decode(instance['public_key']['y']))
    
    # Decode signatures
    signatures = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # ECDSA parameters for secp256r1 (P-256)
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Look for duplicate r values (nonce reuse attack)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_map:
            # Found duplicate r - we can recover the private key
            j = r_map[r]
            r1, s1, z1 = signatures[j]
            r2, s2, z2 = signatures[i]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s * k - z) / r mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Recover private key using first signature
            d = (((s1 * k - z1) % n) * modinv(r1, n)) % n
            
            # Output result
            result = {"d": int_to_hex(d)}
            print(json.dumps(result))
            return
        
        r_map[r] = i
    
    # If no duplicate r found, should not happen in this instance
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()
