import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
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

def point_add(p1, p2, p, a):
    """Add two points on elliptic curve"""
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    
    x1, y1 = p1
    x2, y2 = p2
    
    if x1 == x2:
        if y1 == y2:
            # Point doubling
            s = (3 * x1 * x1 + a) * modinv(2 * y1, p) % p
        else:
            return None  # Point at infinity
    else:
        s = (y2 - y1) * modinv(x2 - x1, p) % p
    
    x3 = (s * s - x1 - x2) % p
    y3 = (s * (x1 - x3) - y1) % p
    
    return (x3, y3)

def point_multiply(k, point, p, a):
    """Multiply point by scalar k using double-and-add"""
    if k == 0:
        return None
    if k < 0:
        raise ValueError("Scalar must be non-negative")
    
    result = None
    addend = point
    
    while k:
        if k & 1:
            result = point_add(result, addend, p, a)
        addend = point_add(addend, addend, p, a)
        k >>= 1
    
    return result

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

signatures = instance['signatures']
public_key = instance['public_key']

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
a = 0
b = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

# Find nonce reuse (same r value)
r_map = {}
for i, sig in enumerate(signatures):
    r = sig['r']
    if r in r_map:
        # Found reuse!
        i1 = r_map[r]
        i2 = i
        
        r_val = int(r, 16)
        s1 = int(signatures[i1]['s'], 16)
        s2 = int(signatures[i2]['s'], 16)
        z1 = int(signatures[i1]['z'], 16)
        z2 = int(signatures[i2]['z'], 16)
        
        # Recover nonce k
        k_nonce = ((z1 - z2) % n) * modinv((s1 - s2) % n, n) % n
        
        # Recover private key d
        d = (s1 * k_nonce - z1) * modinv(r_val, n) % n
        
        break
    r_map[r] = i

# Compute shared secret using ECDH: k = d * Q where Q is the public key
Qx = int(public_key['x'], 16)
Qy = int(public_key['y'], 16)
Q = (Qx, Qy)

# Compute k = d * Q
shared_point = point_multiply(d, Q, p, a)
k_x = shared_point[0]

# Format output
d_hex = format(d, '064x')
k_hex = format(k_x, '064x')

print(json.dumps({"d": d_hex, "k": k_hex}))
