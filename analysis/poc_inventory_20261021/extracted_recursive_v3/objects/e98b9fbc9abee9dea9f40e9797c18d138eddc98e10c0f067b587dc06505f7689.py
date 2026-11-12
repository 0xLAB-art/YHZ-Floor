import json
import sys
import base64
import hashlib
from collections import defaultdict

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def decode_base64_int(b64_str):
    """Decode base64 string to integer"""
    decoded = base64.b64decode(b64_str)
    return int.from_bytes(decoded, byteorder='big')

def int_to_hex(n):
    """Convert integer to 64-character lowercase hex string"""
    hex_str = hex(n)[2:]
    return hex_str.zfill(64)

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    Qx = decode_base64_int(data['public_key']['x'])
    Qy = decode_base64_int(data['public_key']['y'])
    
    # Parse signatures
    signatures = []
    for sig in data['signatures']:
        r = decode_base64_int(sig['r'])
        s = decode_base64_int(sig['s'])
        z = decode_base64_int(sig['z'])
        signatures.append((r, s, z))
    
    # Look for duplicate r values (nonce reuse)
    r_dict = defaultdict(list)
    for i, (r, s, z) in enumerate(signatures):
        r_dict[r].append((i, s, z))
    
    # Find nonce reuse
    k_found = None
    d_found = None
    
    for r, sigs in r_dict.items():
        if len(sigs) >= 2:
            # Nonce reuse detected
            idx1, s1, z1 = sigs[0]
            idx2, s2, z2 = sigs[1]
            
            # Calculate k from two signatures with same r
            # k = (z1 - z2) / (s1 - s2) mod n
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff != 0:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Calculate d from k
                # s = k^-1 * (z + r*d) mod n
                # k*s = z + r*d mod n
                # d = (k*s - z) / r mod n
                k_inv = modinv(k, n)
                r_inv = modinv(r, n)
                d = (r_inv * ((k * s1 - z1) % n)) % n
                
                k_found = k
                d_found = d
                break
    
    # Output result
    result = {
        "d": int_to_hex(d_found),
        "k": int_to_hex(k_found)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()