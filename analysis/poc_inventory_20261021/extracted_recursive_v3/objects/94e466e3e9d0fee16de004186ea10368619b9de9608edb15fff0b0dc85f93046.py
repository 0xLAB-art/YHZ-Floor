import json
import sys
from hashlib import sha256

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

def recover_private_key(sig1, sig2, public_key, p, n, G):
    """Recover private key from two signatures with the same r (nonce reuse)."""
    r1, s1, z1 = sig1
    r2, s2, z2 = sig2
    
    if r1 != r2:
        return None
    
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None
    
    k = (numerator * modinv(denominator, n)) % n
    
    # d = (s1 * k - z1) / r1 mod n
    numerator = (s1 * k - z1) % n
    d = (numerator * modinv(r1, n)) % n
    
    return d

def point_multiply(k, P, p, a):
    """Scalar multiplication of point P by k on elliptic curve."""
    if k == 0:
        return None
    
    if k < 0:
        raise ValueError("Negative scalar")
    
    result = None
    addend = P
    
    while k:
        if k & 1:
            result = point_add(result, addend, p, a)
        addend = point_add(addend, addend, p, a)
        k >>= 1
    
    return result

def point_add(P, Q, p, a):
    """Add two points on elliptic curve."""
    if P is None:
        return Q
    if Q is None:
        return P
    
    x1, y1 = P
    x2, y2 = Q
    
    if x1 == x2:
        if y1 == y2:
            # Point doubling
            s = (3 * x1 * x1 + a) * modinv(2 * y1, p) % p
        else:
            return None
    else:
        # Point addition
        s = (y2 - y1) * modinv(x2 - x1, p) % p
    
    x3 = (s * s - x1 - x2) % p
    y3 = (s * (x1 - x3) - y1) % p
    
    return (x3, y3)

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode public key
    import base64
    pub_x = int.from_bytes(base64.b64decode(instance['public_key']['x']), 'big')
    pub_y = int.from_bytes(base64.b64decode(instance['public_key']['y']), 'big')
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    a = 0
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    G = (Gx, Gy)
    
    # Decode signatures
    signatures = []
    for sig in instance['signatures']:
        r = int.from_bytes(base64.b64decode(sig['r']), 'big')
        s = int.from_bytes(base64.b64decode(sig['s']), 'big')
        z = int.from_bytes(base64.b64decode(sig['z']), 'big')
        signatures.append((r, s, z))
    
    # Find signatures with same r value
    d = None
    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            if signatures[i][0] == signatures[j][0]:
                d = recover_private_key(signatures[i], signatures[j], (pub_x, pub_y), p, n, G)
                if d is not None:
                    # Verify the private key
                    computed_pub = point_multiply(d, G, p, a)
                    if computed_pub == (pub_x, pub_y):
                        break
        if d is not None:
            break
    
    # Format output
    d_hex = format(d, '064x')
    print(json.dumps({"d": d_hex}))

if __name__ == "__main__":
    main()