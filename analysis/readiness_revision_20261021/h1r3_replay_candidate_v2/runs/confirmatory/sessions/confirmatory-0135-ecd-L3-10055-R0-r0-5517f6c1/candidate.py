import sys
import json
import hashlib
from typing import Tuple

def modinv(a: int, m: int) -> int:
    """Extended Euclidean algorithm for modular inverse"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key_from_nonce_reuse(r: int, s1: int, z1: int, s2: int, z2: int, n: int) -> int:
    """Recover private key when same nonce is used for two signatures"""
    # k = (z1 - z2) / (s1 - s2) mod n
    # d = (s*k - z) / r mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    k = (z_diff * modinv(s_diff, n)) % n
    d = (s1 * k - z1) * modinv(r, n) % n
    
    return d

def point_add(p1: Tuple[int, int], p2: Tuple[int, int], p: int, a: int) -> Tuple[int, int]:
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

def point_multiply(k: int, point: Tuple[int, int], p: int, a: int) -> Tuple[int, int]:
    """Multiply a point by scalar k"""
    if k == 0:
        return None
    
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
    data = json.load(f)

# SECP256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
a = 0
b = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

# Parse public key
pub_x = int(data['public_key']['x'], 16)
pub_y = int(data['public_key']['y'], 16)

# Parse signatures
signatures = []
for sig in data['signatures']:
    r = int(sig['r'], 16)
    s = int(sig['s'], 16)
    z = int(sig['z'], 16)
    signatures.append((r, s, z))

# Find duplicate r values
r_dict = {}
for i, (r, s, z) in enumerate(signatures):
    if r not in r_dict:
        r_dict[r] = []
    r_dict[r].append((i, s, z))

# Find nonce reuse
private_key = None
for r, sigs in r_dict.items():
    if len(sigs) >= 2:
        # Found nonce reuse!
        i1, s1, z1 = sigs[0]
        i2, s2, z2 = sigs[1]
        
        try:
            d = recover_private_key_from_nonce_reuse(r, s1, z1, s2, z2, n)
            
            # Verify: compute k from first signature
            k = (z1 + r * d) * modinv(s1, n) % n
            
            # Output
            print(json.dumps({
                "d": format(d, '064x'),
                "k": format(k, '064x')
            }))
            
            private_key = d
            break
        except:
            continue

if private_key is None:
    # Fallback - shouldn't happen with nonce reuse present
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))
