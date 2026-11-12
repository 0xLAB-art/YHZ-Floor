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

def decode_base64_int(s: str) -> int:
    """Decode a base64 string to an integer."""
    return int.from_bytes(base64.b64decode(s), 'big')

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
    
    # ECDSA uses secp256k1 curve
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Look for nonce reuse attack: two signatures with same r
    r_to_sigs = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((s, z, i))
    
    # Find duplicate r values
    d = None
    for r, sigs in r_to_sigs.items():
        if len(sigs) >= 2:
            # We have nonce reuse!
            s1, z1, _ = sigs[0]
            s2, z2, _ = sigs[1]
            
            # From ECDSA:
            # s1 = k^(-1) * (z1 + r*d) mod n
            # s2 = k^(-1) * (z2 + r*d) mod n
            # 
            # s1 - s2 = k^(-1) * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            # 
            # Then: d = (s*k - z) / r mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
            
            # Compute k
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Compute d from first signature
            s1_inv = modinv(s1, n)
            d = (s1_inv * (k * s1 - z1)) % n
            
            # Verify with second signature
            s2_inv = modinv(s2, n)
            d_verify = (s2_inv * (k * s2 - z2)) % n
            
            if d == d_verify and d != 0:
                break
            
            # Try alternative: d = (s*k - z) * r^(-1) mod n
            r_inv = modinv(r, n)
            d = ((s1 * k - z1) * r_inv) % n
            d_verify = ((s2 * k - z2) * r_inv) % n
            
            if d == d_verify and d != 0:
                break
    
    # Format output
    d_hex = format(d, '064x')
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()