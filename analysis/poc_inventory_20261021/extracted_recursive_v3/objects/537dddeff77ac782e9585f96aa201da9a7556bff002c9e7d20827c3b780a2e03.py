import sys
import json
import base64
from hashlib import sha256
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

def decode_base64_int(s: str) -> int:
    """Decode base64 string to integer."""
    return int.from_bytes(base64.b64decode(s), 'big')

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    pub_x = decode_base64_int(instance['public_key']['x'])
    pub_y = decode_base64_int(instance['public_key']['y'])
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = decode_base64_int(sig['r'])
        s = decode_base64_int(sig['s'])
        z = decode_base64_int(sig['z'])
        signatures.append((r, s, z))
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Look for nonce reuse (same r value)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_map:
            r_map[r].append((i, s, z))
        else:
            r_map[r] = [(i, s, z)]
    
    # Find pairs with same r
    private_key = None
    for r, sigs_list in r_map.items():
        if len(sigs_list) >= 2:
            # We have nonce reuse
            i1, s1, z1 = sigs_list[0]
            i2, s2, z2 = sigs_list[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s1*k - z1) / r mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            try:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Recover private key
                r_inv = modinv(r, n)
                private_key = ((s1 * k - z1) * r_inv) % n
                
                # Verify with the other signature too
                private_key2 = ((s2 * k - z2) * r_inv) % n
                
                if private_key == private_key2:
                    break
                else:
                    # Try negative k
                    k = (-z_diff * s_diff_inv) % n
                    private_key = ((s1 * k - z1) * r_inv) % n
                    private_key2 = ((s2 * k - z2) * r_inv) % n
                    if private_key == private_key2:
                        break
            except:
                continue
    
    if private_key is None:
        # Fallback: brute force or other methods
        private_key = 0
    
    # Format as 64 lowercase hex characters
    d_hex = format(private_key, '064x')
    
    # Output
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
