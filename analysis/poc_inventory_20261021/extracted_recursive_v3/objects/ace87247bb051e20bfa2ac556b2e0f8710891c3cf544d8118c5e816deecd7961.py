import base64
import json
import sys

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
    
    # NIST P-256 parameters
    p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
    n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
    
    # Decode public key
    x = int.from_bytes(base64.b64decode(instance['public_key']['x']), 'big')
    y = int.from_bytes(base64.b64decode(instance['public_key']['y']), 'big')
    
    # Decode signatures
    sig1 = instance['signatures'][0]
    r1 = int.from_bytes(base64.b64decode(sig1['r']), 'big')
    s1 = int.from_bytes(base64.b64decode(sig1['s']), 'big')
    z1 = int.from_bytes(base64.b64decode(sig1['z']), 'big')
    
    sig2 = instance['signatures'][1]
    r2 = int.from_bytes(base64.b64decode(sig2['r']), 'big')
    s2 = int.from_bytes(base64.b64decode(sig2['s']), 'big')
    z2 = int.from_bytes(base64.b64decode(sig2['z']), 'big')
    
    # Check if r1 == r2 (nonce reuse attack)
    if r1 == r2:
        # k = (z1 - z2) / (s1 - s2) mod n
        # d = (s1 * k - z1) / r1 mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        k = (z_diff * modinv(s_diff, n)) % n
        
        # Calculate private key d
        d = ((s1 * k - z1) * modinv(r1, n)) % n
        
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        
        result = {"d": d_hex}
        print(json.dumps(result))
    else:
        # No nonce reuse detected
        print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()