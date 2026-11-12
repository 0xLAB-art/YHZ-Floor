import json
import sys
import hashlib
from typing import Tuple
import base64

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

def decode_base64_to_int(s: str) -> int:
    """Decode base64 string to integer."""
    return int.from_bytes(base64.b64decode(s), 'big')

def main():
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
    
    # Determine curve parameters from public key
    # Try secp256k1: y^2 = x^3 + 7 (mod p)
    p_secp256k1 = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n_secp256k1 = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Verify it's secp256k1
    y2 = (y * y) % p_secp256k1
    x3_plus_7 = (x * x * x + 7) % p_secp256k1
    
    if y2 == x3_plus_7:
        n = n_secp256k1
    else:
        # Try secp256r1 or other curves if needed
        # For now assume secp256k1
        n = n_secp256k1
    
    # Look for nonce reuse (same r value with different messages)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_map:
            # Found reuse! Extract private key
            j = r_map[r]
            r1, s1, z1 = signatures[j]
            r2, s2, z2 = signatures[i]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s*k - z) / r mod n
            
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
                
            k = (numerator * modinv(denominator, n)) % n
            
            # Now compute private key d
            d = ((s1 * k - z1) * modinv(r1, n)) % n
            
            # Format as 64 lowercase hex characters
            d_hex = format(d, '064x')
            
            print(json.dumps({"d": d_hex}))
            return
        else:
            r_map[r] = i
    
    # If no nonce reuse found, this shouldn't happen based on the problem
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()