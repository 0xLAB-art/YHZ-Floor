import sys
import json
import base64
from collections import defaultdict
from math import gcd

def mod_inverse(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    if gcd(a, m) != 1:
        return None
    u1, u2, u3 = 1, 0, a
    v1, v2, v3 = 0, 1, m
    while v3 != 0:
        q = u3 // v3
        v1, v2, v3, u1, u2, u3 = (u1 - q * v1), (u2 - q * v2), (u3 - q * v3), v1, v2, v3
    return u1 % m

def bytes_to_int(b):
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    """Convert integer to 64-character hex string."""
    return format(n, '064x')

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    pub_x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
    pub_y = bytes_to_int(base64.b64decode(instance['public_key']['y']))
    
    # ECDSA uses secp256k1 curve
    # Curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # Look for repeated r values (nonce reuse attack)
    r_groups = defaultdict(list)
    for i, (r, s, z) in enumerate(signatures):
        r_groups[r].append((s, z, i))
    
    # Find r value that appears multiple times
    for r, group in r_groups.items():
        if len(group) >= 2:
            # We have nonce reuse!
            s1, z1, idx1 = group[0]
            s2, z2, idx2 = group[1]
            
            # From ECDSA:
            # s1 = k^-1 * (z1 + r*d) mod n
            # s2 = k^-1 * (z2 + r*d) mod n
            #
            # s1 - s2 = k^-1 * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            s_diff_inv = mod_inverse(s_diff, n)
            if s_diff_inv is None:
                continue
            
            k = (z_diff * s_diff_inv) % n
            
            # Now recover d from: s = k^-1 * (z + r*d) mod n
            # s * k = z + r*d mod n
            # r*d = s*k - z mod n
            # d = (s*k - z) / r mod n
            
            k_inv = mod_inverse(k, n)
            if k_inv is None:
                continue
            
            r_inv = mod_inverse(r, n)
            if r_inv is None:
                continue
            
            d = ((s1 * k - z1) * r_inv) % n
            
            # Output result
            result = {"d": int_to_hex(d)}
            print(json.dumps(result))
            return
    
    # No solution found
    result = {"d": "0" * 64}
    print(json.dumps(result))

if __name__ == "__main__":
    main()