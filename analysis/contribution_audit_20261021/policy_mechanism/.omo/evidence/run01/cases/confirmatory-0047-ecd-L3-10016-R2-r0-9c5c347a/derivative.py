import json
import sys
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

def int_to_hex64(n: int) -> str:
    """Convert integer to 64-character lowercase hex string."""
    hex_str = hex(n)[2:].rstrip('L')
    return hex_str.zfill(64)

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    Qx = decode_base64_to_int(instance['public_key']['x'])
    Qy = decode_base64_to_int(instance['public_key']['y'])
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = decode_base64_to_int(sig['r'])
        s = decode_base64_to_int(sig['s'])
        z = decode_base64_to_int(sig['z'])
        signatures.append((r, s, z))
    
    # Look for nonce reuse (same r value in different signatures)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find pairs with same r
    d = None
    k = None
    
    for r, sigs in r_map.items():
        if len(sigs) >= 2:
            # We have nonce reuse!
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s*k - z) / r mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            try:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Verify with first signature
                r_inv = modinv(r, n)
                d = ((s1 * k - z1) * r_inv) % n
                
                # Verify with public key: Q = d*G
                # We can verify by checking if s*k - z == r*d (mod n)
                # Or by checking signature validity
                
                break
            except ValueError:
                continue
    
    # If no nonce reuse found, try other attacks
    if d is None:
        # Try biased nonce attack or lattice attack
        # For this challenge, nonce reuse is most likely
        pass
    
    result = {
        "d": int_to_hex64(d),
        "k": int_to_hex64(k)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
