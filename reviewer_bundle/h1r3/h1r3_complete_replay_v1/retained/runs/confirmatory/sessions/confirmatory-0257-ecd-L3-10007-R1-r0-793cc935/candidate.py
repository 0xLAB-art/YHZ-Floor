import json
import sys
import hashlib

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
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
    """Multiply a point by scalar k using double-and-add"""
    if k == 0:
        return None
    if k < 0:
        raise ValueError("Negative scalar not supported")
    
    result = None
    addend = point
    
    while k:
        if k & 1:
            result = point_add(result, addend, p, a)
        addend = point_add(addend, addend, p, a)
        k >>= 1
    
    return result

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
a = 0

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

signatures = data['signatures']
pub_x = int(data['public_key']['x'], 16)
pub_y = int(data['public_key']['y'], 16)
public_key = (pub_x, pub_y)

# Find signatures with same r
r_to_indices = {}
for i, sig in enumerate(signatures):
    r = sig['r']
    if r not in r_to_indices:
        r_to_indices[r] = []
    r_to_indices[r].append(i)

# Find pair with same r
for r_hex, indices in r_to_indices.items():
    if len(indices) >= 2:
        i, j = indices[0], indices[1]
        
        r = int(signatures[i]['r'], 16)
        s1 = int(signatures[i]['s'], 16)
        z1 = int(signatures[i]['z'], 16)
        s2 = int(signatures[j]['s'], 16)
        z2 = int(signatures[j]['z'], 16)
        
        # Calculate k = (z1 - z2) / (s1 - s2) mod n
        k = ((z1 - z2) * modinv(s1 - s2, n)) % n
        
        # Calculate d = (s*k - z) / r mod n
        d = ((s1 * k - z1) * modinv(r, n)) % n
        
        # Verify: check if d*G = public_key
        computed_pub = point_multiply(d, G, p, a)
        
        if computed_pub == public_key:
            # Correct! This is signature i's nonce
            result_d = d
            result_k = k
            break
        else:
            # Try the other signature's nonce
            k2 = ((z2 - z1) * modinv(s2 - s1, n)) % n
            d2 = ((s2 * k2 - z2) * modinv(r, n)) % n
            
            computed_pub2 = point_multiply(d2, G, p, a)
            if computed_pub2 == public_key:
                result_d = d2
                result_k = k2
                break

# Output result
output = {
    "d": format(result_d, '064x'),
    "k": format(result_k, '064x')
}
print(json.dumps(output))
