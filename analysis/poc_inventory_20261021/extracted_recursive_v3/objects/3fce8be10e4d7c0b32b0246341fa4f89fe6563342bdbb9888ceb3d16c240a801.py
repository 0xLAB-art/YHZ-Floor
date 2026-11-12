import sys
import json
import base64
from typing import List, Tuple

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

def decode_base64_to_int(b64_str: str) -> int:
    """Decode base64 string to integer."""
    decoded = base64.b64decode(b64_str)
    return int.from_bytes(decoded, byteorder='big')

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    x = decode_base64_to_int(instance['public_key']['x'])
    y = decode_base64_to_int(instance['public_key']['y'])
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = decode_base64_to_int(sig['r'])
        s = decode_base64_to_int(sig['s'])
        z = decode_base64_to_int(sig['z'])
        signatures.append((r, s, z))
    
    # ECDSA uses secp256k1 curve parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Look for nonce reuse (same r value)
    # If two signatures share the same r, they used the same k (nonce)
    # We can recover the private key d using:
    # k = (z1 - z2) / (s1 - s2) mod n
    # d = (s*k - z) / r mod n
    
    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            r1, s1, z1 = signatures[i]
            r2, s2, z2 = signatures[j]
            
            if r1 == r2:
                # Found nonce reuse!
                # Calculate k
                numerator = (z1 - z2) % n
                denominator = (s1 - s2) % n
                
                if denominator == 0:
                    continue
                
                k = (numerator * modinv(denominator, n)) % n
                
                # Calculate private key d using first signature
                # d = (s*k - z) / r mod n
                d = ((s1 * k - z1) % n * modinv(r1, n)) % n
                
                # Convert to hex
                d_hex = format(d, '064x')
                
                # Output result
                print(json.dumps({"d": d_hex}))
                return
    
    # If no nonce reuse found, should not happen in this instance
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()