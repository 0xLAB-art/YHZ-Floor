import json
import sys

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m

def egcd(a, b):
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = egcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(signatures, public_key, p, n, G):
    """Recover private key from signatures with repeated nonces."""
    # Group signatures by r value to find nonce reuse
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(sig)
    
    # Find pairs with same r
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            s1 = int(sigs[0]['s'], 16)
            z1 = int(sigs[0]['z'], 16)
            s2 = int(sigs[1]['s'], 16)
            z2 = int(sigs[1]['z'], 16)
            
            # Recover nonce k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            denom_inv = modinv(denominator, n)
            if denom_inv is None:
                continue
            
            k = (numerator * denom_inv) % n
            
            # Recover private key d: d = (s * k - z) / r mod n
            r_inv = modinv(r, n)
            if r_inv is None:
                continue
            
            d = ((s1 * k - z1) % n * r_inv) % n
            
            # Verify the private key
            Gx, Gy = G
            Qx = int(public_key['x'], 16)
            Qy = int(public_key['y'], 16)
            
            # Check if d * G = Q
            calc_x, calc_y = scalar_mult(d, Gx, Gy, p, n)
            if calc_x == Qx and calc_y == Qy:
                return d, k
    
    return None, None

def scalar_mult(k, x, y, p, n):
    """Scalar multiplication on elliptic curve using double-and-add."""
    if k == 0:
        return None, None
    if k == 1:
        return x, y
    
    # Use binary method
    result_x, result_y = None, None
    addend_x, addend_y = x, y
    
    while k:
        if k & 1:
            if result_x is None:
                result_x, result_y = addend_x, addend_y
            else:
                result_x, result_y = point_add(result_x, result_y, addend_x, addend_y, p)
        addend_x, addend_y = point_double(addend_x, addend_y, p)
        k >>= 1
    
    return result_x, result_y

def point_double(x, y, p):
    """Double a point on secp256k1."""
    # a = 0 for secp256k1
    # s = (3 * x^2) / (2 * y) mod p
    s = (3 * x * x % p) * modinv(2 * y, p) % p
    x_new = (s * s - 2 * x) % p
    y_new = (s * (x - x_new) - y) % p
    return x_new, y_new

def point_add(x1, y1, x2, y2, p):
    """Add two points on secp256k1."""
    if x1 == x2 and y1 == y2:
        return point_double(x1, y1, p)
    
    # s = (y2 - y1) / (x2 - x1) mod p
    s = ((y2 - y1) % p) * modinv((x2 - x1) % p, p) % p
    x3 = (s * s - x1 - x2) % p
    y3 = (s * (x1 - x3) - y1) % p
    return x3, y3

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

public_key = instance['public_key']
signatures = instance['signatures']

# Recover private key
d, k = recover_private_key(signatures, public_key, p, n, G)

# Format output
d_hex = format(d, '064x')
k_hex = format(k, '064x')

print(json.dumps({"d": d_hex, "k": k_hex}))
