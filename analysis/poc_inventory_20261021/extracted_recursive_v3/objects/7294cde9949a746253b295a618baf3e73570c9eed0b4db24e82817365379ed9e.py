import sys
import json
import base64
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

def decode_base64_to_int(b64_str: str) -> int:
    """Decode base64 string to integer."""
    data = base64.b64decode(b64_str)
    return int.from_bytes(data, byteorder='big')

def recover_private_key_from_nonce_reuse(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> int:
    """
    Recover private key when nonce k is reused in two signatures.
    
    ECDSA signatures: s = k^(-1) * (z + r*d) mod n
    If same k (thus same r) is used:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    Therefore:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    # Calculate k from the two signatures
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None
    
    k = (numerator * modinv(denominator, n)) % n
    
    # Calculate private key d
    d = (((s1 * k - z1) % n) * modinv(r, n)) % n
    
    return k, d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    pub_x = decode_base64_to_int(instance['public_key']['x'])
    pub_y = decode_base64_to_int(instance['public_key']['y'])
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = decode_base64_to_int(sig['r'])
        s = decode_base64_to_int(sig['s'])
        z = decode_base64_to_int(sig['z'])
        signatures.append((r, s, z))
    
    # Look for nonce reuse (same r value)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_map:
            # Found reuse!
            j, s_prev, z_prev = r_map[r]
            
            # Recover private key
            result = recover_private_key_from_nonce_reuse(r, s, s_prev, z, z_prev, n)
            if result:
                k, d = result
                
                # Format output
                d_hex = format(d, '064x')
                k_hex = format(k, '064x')
                
                output = {
                    "d": d_hex,
                    "k": k_hex
                }
                print(json.dumps(output))
                return
        else:
            r_map[r] = (i, s, z)
    
    # Should not reach here if there's nonce reuse
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()