import json
import sys
import hashlib
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

def base64_to_int(b64_str: str) -> int:
    """Convert base64 string to integer."""
    import base64
    decoded = base64.b64decode(b64_str)
    return int.from_bytes(decoded, byteorder='big')

def recover_private_key(signatures: list, pub_key: dict) -> str:
    """
    Recover ECDSA private key from signatures with repeated nonces.
    Uses the secp256k1 curve parameters.
    """
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    sigs = []
    for sig in signatures:
        r = base64_to_int(sig['r'])
        s = base64_to_int(sig['s'])
        z = base64_to_int(sig['z'])
        sigs.append({'r': r, 's': s, 'z': z})
    
    # Find signatures with the same r value (same nonce k)
    r_groups = {}
    for i, sig in enumerate(sigs):
        r = sig['r']
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(i)
    
    # Find a pair of signatures with the same r
    for r_val, indices in r_groups.items():
        if len(indices) >= 2:
            # Use the first two signatures with the same r
            i1, i2 = indices[0], indices[1]
            sig1, sig2 = sigs[i1], sigs[i2]
            
            r = sig1['r']
            s1, s2 = sig1['s'], sig2['s']
            z1, z2 = sig1['z'], sig2['z']
            
            # Recover k: k = (z1 - z2) / (s1 - s2) mod n
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            try:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Recover private key d: d = (s*k - z) / r mod n
                r_inv = modinv(r, n)
                d = ((s1 * k - z1) * r_inv) % n
                
                # Verify with the second signature
                d_verify = ((s2 * k - z2) * r_inv) % n
                
                if d == d_verify and d != 0:
                    # Convert to 64 hex characters (32 bytes)
                    d_hex = format(d, '064x')
                    return d_hex
            except ValueError:
                continue
    
    # If no repeated r found, return a placeholder (shouldn't happen with valid input)
    return "0" * 64

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Extract data
    public_key = instance['public_key']
    signatures = instance['signatures']
    
    # Recover private key
    d = recover_private_key(signatures, public_key)
    
    # Output result
    result = {"d": d}
    print(json.dumps(result))

if __name__ == "__main__":
    main()