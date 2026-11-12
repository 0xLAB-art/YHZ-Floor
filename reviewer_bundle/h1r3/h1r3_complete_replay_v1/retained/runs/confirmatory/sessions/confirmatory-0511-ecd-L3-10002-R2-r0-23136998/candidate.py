import sys
import json
import base64
import hashlib
from collections import defaultdict

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_bytes(n, length):
    return n.to_bytes(length, 'big')

def mod_inverse(a, m):
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode public key
    pub_x = base64.b64decode(instance['public_key']['x'])
    pub_y = base64.b64decode(instance['public_key']['y'])
    
    Qx = bytes_to_int(pub_x)
    Qy = bytes_to_int(pub_y)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode signatures
    signatures = []
    for sig in instance['signatures']:
        r_bytes = base64.b64decode(sig['r'])
        s_bytes = base64.b64decode(sig['s'])
        z_bytes = base64.b64decode(sig['z'])
        
        r = bytes_to_int(r_bytes)
        s = bytes_to_int(s_bytes)
        z = bytes_to_int(z_bytes)
        
        signatures.append((r, s, z))
    
    # Look for nonce reuse (same r value)
    r_groups = defaultdict(list)
    for i, (r, s, z) in enumerate(signatures):
        r_groups[r].append((i, s, z))
    
    # Find k and d from nonce reuse
    k = None
    d = None
    
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            # From ECDSA: s = k^(-1) * (z + r*d) mod n
            # s1 = k^(-1) * (z1 + r*d) mod n
            # s2 = k^(-1) * (z2 + r*d) mod n
            # 
            # s1 - s2 = k^(-1) * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff != 0:
                s_diff_inv = mod_inverse(s_diff, n)
                k_candidate = (z_diff * s_diff_inv) % n
                
                # Verify and recover d
                # s1 = k^(-1) * (z1 + r*d) mod n
                # k * s1 = z1 + r*d mod n
                # d = (k * s1 - z1) / r mod n
                
                k_inv = mod_inverse(k_candidate, n)
                r_inv = mod_inverse(r, n)
                d_candidate = ((k_candidate * s1 - z1) * r_inv) % n
                
                # Verify with second signature
                expected_s2 = (k_inv * (z2 + r * d_candidate)) % n
                if expected_s2 == s2:
                    k = k_candidate
                    d = d_candidate
                    break
    
    # Format output
    k_hex = format(k, '064x')
    d_hex = format(d, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
