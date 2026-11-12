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

def int_to_hex(n: int) -> str:
    """Convert integer to 64-character lowercase hex string."""
    hex_str = hex(n)[2:]
    return hex_str.zfill(64)

# SECP256k1 parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
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
    
    # Look for nonce reuse (same r value in different signatures)
    r_dict = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_dict:
            r_dict[r] = []
        r_dict[r].append((i, s, z))
    
    # Find a pair with the same r
    k = None
    d = None
    
    for r, sig_list in r_dict.items():
        if len(sig_list) >= 2:
            # We have nonce reuse!
            i1, s1, z1 = sig_list[0]
            i2, s2, z2 = sig_list[1]
            
            # From ECDSA: s = (z + r*d) / k mod n
            # s1 = (z1 + r*d) / k mod n
            # s2 = (z2 + r*d) / k mod n
            # s1 - s2 = (z1 - z2) / k mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % N
            z_diff = (z1 - z2) % N
            
            if s_diff != 0:
                s_diff_inv = modinv(s_diff, N)
                k = (z_diff * s_diff_inv) % N
                
                # Now recover d from k
                # s1 = (z1 + r*d) / k mod n
                # s1 * k = z1 + r*d mod n
                # r*d = s1*k - z1 mod n
                # d = (s1*k - z1) / r mod n
                
                r_inv = modinv(r, N)
                d = ((s1 * k - z1) * r_inv) % N
                
                break
    
    # Output result
    result = {
        "d": int_to_hex(d),
        "k": int_to_hex(k)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
