import sys
import json
import base64
from typing import Tuple

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

def decode_base64_int(s: str) -> int:
    """Decode base64 string to integer."""
    b = base64.b64decode(s)
    return int.from_bytes(b, byteorder='big')

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # Decode public key
    x = decode_base64_int(data['public_key']['x'])
    y = decode_base64_int(data['public_key']['y'])
    
    # Decode signatures
    signatures = []
    for sig in data['signatures']:
        r = decode_base64_int(sig['r'])
        s = decode_base64_int(sig['s'])
        z = decode_base64_int(sig['z'])
        signatures.append((r, s, z))
    
    # ECDSA uses secp256k1 curve parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find two signatures with the same r value (nonce reuse)
    r_dict = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_dict:
            # Found duplicate r, extract private key
            j = r_dict[r]
            r1, s1, z1 = signatures[j]
            r2, s2, z2 = signatures[i]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s*k - z) / r mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Calculate private key d
            d = (((s1 * k - z1) % n) * modinv(r1, n)) % n
            
            # Format as 64 lowercase hex characters
            d_hex = format(d, '064x')
            
            result = {"d": d_hex}
            print(json.dumps(result))
            return
        
        r_dict[r] = i
    
    # Should not reach here if instance is valid
    raise ValueError("No nonce reuse found")

if __name__ == "__main__":
    main()