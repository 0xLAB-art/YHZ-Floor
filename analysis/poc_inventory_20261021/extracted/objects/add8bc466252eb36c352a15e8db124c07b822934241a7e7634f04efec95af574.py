import json
import sys
import base64

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
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
    
    # P-256 (secp256r1) parameters
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Decode signatures
    sig1 = instance['signatures'][0]
    sig2 = instance['signatures'][1]
    
    r1 = int.from_bytes(base64.b64decode(sig1['r']), 'big')
    s1 = int.from_bytes(base64.b64decode(sig1['s']), 'big')
    z1 = int.from_bytes(base64.b64decode(sig1['z']), 'big')
    
    r2 = int.from_bytes(base64.b64decode(sig2['r']), 'big')
    s2 = int.from_bytes(base64.b64decode(sig2['s']), 'big')
    z2 = int.from_bytes(base64.b64decode(sig2['z']), 'big')
    
    # Verify r values are the same (nonce reuse)
    assert r1 == r2
    r = r1
    
    # Recover nonce k from two signatures with same r
    # k = (z1 - z2) / (s1 - s2) mod n
    k = ((z1 - z2) % n) * modinv((s1 - s2) % n, n) % n
    
    # Recover private key d
    # d = (s*k - z) / r mod n
    d = ((s1 * k - z1) % n) * modinv(r, n) % n
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
