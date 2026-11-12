import json
import sys
from hashlib import sha256
from collections import defaultdict

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

def bytes_to_int(b):
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n, length=32):
    """Convert integer to hex string of specified byte length."""
    return format(n, f'0{length*2}x')

# NIST P-256 parameters
p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    import base64
    
    # Parse public key
    pub_x = bytes_to_int(base64.b64decode(data['public_key']['x']))
    pub_y = bytes_to_int(base64.b64decode(data['public_key']['y']))
    
    # Parse signatures
    signatures = []
    for sig in data['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # Look for nonce reuse (same r value)
    r_map = defaultdict(list)
    for i, (r, s, z) in enumerate(signatures):
        r_map[r].append((i, s, z))
    
    # Find pairs with same r
    for r, sigs in r_map.items():
        if len(sigs) >= 2:
            # We have nonce reuse!
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s1 * k - z1) / r mod n
            
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
                
            k = (numerator * modinv(denominator, n)) % n
            
            # Now recover private key d
            # s1 = (z1 + r * d) / k mod n
            # s1 * k = z1 + r * d mod n
            # d = (s1 * k - z1) / r mod n
            
            numerator_d = ((s1 * k) % n - z1) % n
            d = (numerator_d * modinv(r, n)) % n
            
            result = {"d": int_to_hex(d)}
            print(json.dumps(result))
            return
    
    # If no nonce reuse found, output a placeholder
    result = {"d": "0" * 64}
    print(json.dumps(result))

if __name__ == "__main__":
    main()