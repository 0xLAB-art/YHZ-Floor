import json
import sys

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

def point_add(p1, p2, a, p_mod):
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
            s = (3 * x1 * x1 + a) * modinv(2 * y1, p_mod) % p_mod
        else:
            return None  # Point at infinity
    else:
        s = (y2 - y1) * modinv(x2 - x1, p_mod) % p_mod
    
    x3 = (s * s - x1 - x2) % p_mod
    y3 = (s * (x1 - x3) - y1) % p_mod
    
    return (x3, y3)

def point_multiply(k, point, a, p_mod):
    """Multiply point by scalar k using double-and-add"""
    if k == 0:
        return None
    if k == 1:
        return point
    
    result = None
    addend = point
    
    while k:
        if k & 1:
            result = point_add(result, addend, a, p_mod)
        addend = point_add(addend, addend, a, p_mod)
        k >>= 1
    
    return result

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
a = 0
b = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

pub_x = int(data['public_key']['x'], 16)
pub_y = int(data['public_key']['y'], 16)
signatures = data['signatures']

# Find signatures with same r (nonce reuse)
r_map = {}
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with same r
k_found = None
d_found = None

for r_val, indices in r_map.items():
    if len(indices) >= 2:
        i1, i2 = indices[0], indices[1]
        
        r = int(signatures[i1]['r'], 16)
        s1 = int(signatures[i1]['s'], 16)
        z1 = int(signatures[i1]['z'], 16)
        s2 = int(signatures[i2]['s'], 16)
        z2 = int(signatures[i2]['z'], 16)
        
        # Recover k: k = (z1 - z2) / (s1 - s2) mod n
        k = ((z1 - z2) * modinv(s1 - s2, n)) % n
        
        # Recover d: d = (s*k - z) / r mod n
        d = ((s1 * k - z1) * modinv(r, n)) % n
        
        # Verify: G*d should equal public key
        result = point_multiply(d, (Gx, Gy), a, p)
        
        if result and result[0] == pub_x and result[1] == pub_y:
            k_found = k
            d_found = d
            break

# Format output
result = {
    "d": format(d_found, '064x'),
    "k": format(k_found, '064x')
}

print(json.dumps(result))
