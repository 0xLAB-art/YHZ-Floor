import json
import sys

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

def bytes_to_int(b: bytes) -> int:
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n: int) -> str:
    """Convert integer to 64-character hex string."""
    hex_str = hex(n)[2:]
    return hex_str.zfill(64)

def recover_private_key(signatures: List[dict], public_key: dict, p: int, n: int, gx: int, gy: int) -> int:
    """
    Recover private key from ECDSA signatures.
    This exploits nonce reuse or other weaknesses.
    """
    # Check for duplicate r values (nonce reuse)
    r_values = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r in r_values:
            # Found duplicate r - nonce reuse attack
            j = r_values[r]
            return recover_from_nonce_reuse(
                signatures[i], signatures[j], n
            )
        r_values[r] = i
    
    return None

def recover_from_nonce_reuse(sig1: dict, sig2: dict, n: int) -> int:
    """
    Recover private key from two signatures with same nonce (same r).
    
    For ECDSA:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    From these:
    s1 - s2 = k^-1 * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1*k - z1) / r mod n
    """
    r = sig1['r']
    s1 = sig1['s']
    s2 = sig2['s']
    z1 = sig1['z']
    z2 = sig2['z']
    
    # Calculate k (the nonce)
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None
    
    k = (numerator * modinv(denominator, n)) % n
    
    # Calculate d (private key)
    numerator = (s1 * k - z1) % n
    denominator = r % n
    
    if denominator == 0:
        return None
    
    d = (numerator * modinv(denominator, n)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    
    # Parse public key
    import base64
    pub_x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
    pub_y = bytes_to_int(base64.b64decode(instance['public_key']['y']))
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append({'r': r, 's': s, 'z': z})
    
    # Recover private key
    d = recover_private_key(signatures, instance['public_key'], p, n, gx, gy)
    
    # Output result
    result = {"d": int_to_hex(d)}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
