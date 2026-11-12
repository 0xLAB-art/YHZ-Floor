import sys
import json
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

def decode_base64_int(s: str) -> int:
    """Decode base64 string to integer."""
    data = base64.b64decode(s)
    return int.from_bytes(data, byteorder='big')

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    x = decode_base64_int(instance['public_key']['x'])
    y = decode_base64_int(instance['public_key']['y'])
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = decode_base64_int(sig['r'])
        s = decode_base64_int(sig['s'])
        z = decode_base64_int(sig['z'])
        signatures.append((r, s, z))
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Look for signature pairs with the same r value (nonce reuse)
    d = None
    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            r1, s1, z1 = signatures[i]
            r2, s2, z2 = signatures[j]
            
            if r1 == r2:
                # Nonce reuse detected!
                # k = (z1 - z2) / (s1 - s2) mod n
                # d = (s1 * k - z1) / r1 mod n
                
                numerator = (z1 - z2) % n
                denominator = (s1 - s2) % n
                
                if denominator == 0:
                    continue
                
                k = (numerator * modinv(denominator, n)) % n
                
                # Calculate private key
                d_numerator = (s1 * k - z1) % n
                d_denominator = r1 % n
                
                if d_denominator == 0:
                    continue
                
                d = (d_numerator * modinv(d_denominator, n)) % n
                break
        
        if d is not None:
            break
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
