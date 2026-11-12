import sys
import json
from collections import Counter

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

def recover_private_key(r, s1, z1, s2, z2, n):
    """Recover private key from two signatures with same nonce"""
    # k = (z1 - z2) / (s1 - s2) mod n
    # d = (s*k - z) / r mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Now compute private key: d = (s*k - z) / r mod n
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

def point_multiply(x, y, scalar, p, a, n):
    """Scalar multiplication on elliptic curve using double-and-add"""
    if scalar == 0:
        return None, None
    
    if scalar < 0:
        scalar = scalar % n
    
    # Result starts at point at infinity
    result_x, result_y = None, None
    addend_x, addend_y = x, y
    
    while scalar:
        if scalar & 1:
            result_x, result_y = point_add(result_x, result_y, addend_x, addend_y, p, a)
        addend_x, addend_y = point_double(addend_x, addend_y, p, a)
        scalar >>= 1
    
    return result_x, result_y

def point_add(x1, y1, x2, y2, p, a):
    """Add two points on elliptic curve"""
    if x1 is None:
        return x2, y2
    if x2 is None:
        return x1, y1
    
    if x1 == x2:
        if y1 == y2:
            return point_double(x1, y1, p, a)
        else:
            return None, None
    
    # Different points
    slope = ((y2 - y1) * modinv((x2 - x1) % p, p)) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    
    return x3, y3

def point_double(x, y, p, a):
    """Double a point on elliptic curve"""
    if x is None:
        return None, None
    
    # slope = (3*x^2 + a) / (2*y)
    slope = ((3 * x * x + a) * modinv((2 * y) % p, p)) % p
    x3 = (slope * slope - 2 * x) % p
    y3 = (slope * (x - x3) - y) % p
    
    return x3, y3

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
a = 0
b = 7
gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

# Parse public key
pub_x = int(instance['public_key']['x'], 16)
pub_y = int(instance['public_key']['y'], 16)

# Parse signatures
signatures = []
for sig in instance['signatures']:
    r = int(sig['r'], 16)
    s = int(sig['s'], 16)
    z = int(sig['z'], 16)
    signatures.append((r, s, z))

# Check for repeated r values
r_values = [sig[0] for sig in signatures]
r_counts = Counter(r_values)
repeated_r = [r for r, count in r_counts.items() if count > 1]

if repeated_r:
    # Found nonce reuse - recover private key
    r_reused = repeated_r[0]
    
    # Find two signatures with this r
    sigs_with_r = [(s, z) for r, s, z in signatures if r == r_reused]
    s1, z1 = sigs_with_r[0]
    s2, z2 = sigs_with_r[1]
    
    # Recover private key
    d = recover_private_key(r_reused, s1, z1, s2, z2, n)
    
    # Verify by computing public key
    computed_x, computed_y = point_multiply(gx, gy, d, p, a, n)
    
    if computed_x == pub_x and computed_y == pub_y:
        result = {
            "status": "COMPROMISED",
            "private_key": hex(d)[2:].zfill(64)
        }
    else:
        result = {
            "status": "UNDERDETERMINED",
            "reason": "recovered key does not match public key"
        }
else:
    result = {
        "status": "UNDERDETERMINED",
        "reason": "no obvious vulnerability detected"
    }

print(json.dumps(result))
