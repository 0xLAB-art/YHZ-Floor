import sys
import json
import base64
import hashlib

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
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
    
    # Parse public key
    pub_x = int.from_bytes(base64.b64decode(instance['public_key']['x']), 'big')
    pub_y = int.from_bytes(base64.b64decode(instance['public_key']['y']), 'big')
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = int.from_bytes(base64.b64decode(sig['r']), 'big')
        s = int.from_bytes(base64.b64decode(sig['s']), 'big')
        z = int.from_bytes(base64.b64decode(sig['z']), 'big')
        signatures.append((r, s, z))
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Look for nonce reuse (same r value)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_map:
            # Found nonce reuse!
            j = r_map[r]
            r1, s1, z1 = signatures[j]
            r2, s2, z2 = signatures[i]
            
            # Both signatures use the same k (nonce)
            # s1 = k^-1 * (z1 + r1*d) mod n
            # s2 = k^-1 * (z2 + r2*d) mod n
            # Since r1 = r2 = r:
            # s1 - s2 = k^-1 * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            z_diff = (z1 - z2) % n
            s_diff = (s1 - s2) % n
            
            if s_diff == 0:
                continue
            
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Now recover private key d
            # s1 = k^-1 * (z1 + r1*d) mod n
            # s1*k = z1 + r1*d mod n
            # d = (s1*k - z1) / r1 mod n
            
            k_inv = modinv(k, n)
            d = ((s1 * k - z1) * modinv(r1, n)) % n
            
            # Format output
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            print(json.dumps({"d": d_hex, "k": k_hex}))
            return
        
        r_map[r] = i
    
    # If no nonce reuse found, this shouldn't happen for this problem
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()