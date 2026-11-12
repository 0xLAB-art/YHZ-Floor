import sys
import json
import base64
from typing import List, Tuple
from collections import defaultdict

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

def decode_base64_to_int(s: str) -> int:
    """Decode base64 string to integer."""
    b = base64.b64decode(s)
    return int.from_bytes(b, 'big')

def int_to_hex(n: int) -> str:
    """Convert integer to 64-character lowercase hex string."""
    return format(n, '064x')

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # Parse public key
    pub_x = decode_base64_to_int(data['public_key']['x'])
    pub_y = decode_base64_to_int(data['public_key']['y'])
    
    # Parse signatures
    signatures = []
    for sig in data['signatures']:
        r = decode_base64_to_int(sig['r'])
        s = decode_base64_to_int(sig['s'])
        z = decode_base64_to_int(sig['z'])
        signatures.append((r, s, z))
    
    # Look for duplicate r values (nonce reuse attack)
    r_dict = defaultdict(list)
    for i, (r, s, z) in enumerate(signatures):
        r_dict[r].append((i, s, z))
    
    # Find pairs with same r
    for r, pairs in r_dict.items():
        if len(pairs) >= 2:
            # Use first two signatures with same r
            i1, s1, z1 = pairs[0]
            i2, s2, z2 = pairs[1]
            
            # Recover private key using nonce reuse
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s1*k - z1) / r mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            try:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Verify and recover d
                r_inv = modinv(r, n)
                d = (((s1 * k - z1) % n) * r_inv) % n
                
                # Output result
                result = {
                    "d": int_to_hex(d),
                    "k": int_to_hex(k)
                }
                print(json.dumps(result))
                return
                
            except ValueError:
                continue
    
    # If no solution found, output zeros (should not happen with valid input)
    result = {
        "d": "0" * 64,
        "k": "0" * 64
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
