import sys
import json
from collections import Counter

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key_from_nonce_reuse(r, s1, z1, s2, z2, n):
    """Recover private key when same nonce is used for two signatures"""
    # k = (z1 - z2) / (s1 - s2) mod n
    # d = (s * k - z) / r mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    if s_diff_inv is None:
        return None
    
    k = (z_diff * s_diff_inv) % n
    
    # Now recover private key: d = (s1 * k - z1) / r mod n
    r_inv = modinv(r, n)
    if r_inv is None:
        return None
    
    d = (((s1 * k - z1) % n) * r_inv) % n
    
    return d

def point_multiply(x, y, k, p, a, n):
    """Multiply point (x, y) by scalar k on elliptic curve"""
    if k == 0:
        return None, None
    if k == 1:
        return x, y
    
    # Double-and-add algorithm
    result_x, result_y = None, None
    addend_x, addend_y = x, y
    
    while k:
        if k & 1:
            if result_x is None:
                result_x, result_y = addend_x, addend_y
            else:
                result_x, result_y = point_add(result_x, result_y, addend_x, addend_y, p, a)
        addend_x, addend_y = point_double(addend_x, addend_y, p, a)
        k >>= 1
    
    return result_x, result_y

def point_double(x, y, p, a):
    """Double a point on elliptic curve"""
    if y == 0:
        return None, None
    
    # s = (3x^2 + a) / (2y)
    s = ((3 * x * x + a) * modinv(2 * y, p)) % p
    x_new = (s * s - 2 * x) % p
    y_new = (s * (x - x_new) - y) % p
    
    return x_new, y_new

def point_add(x1, y1, x2, y2, p, a):
    """Add two points on elliptic curve"""
    if x1 == x2:
        if y1 == y2:
            return point_double(x1, y1, p, a)
        else:
            return None, None
    
    # s = (y2 - y1) / (x2 - x1)
    s = ((y2 - y1) * modinv((x2 - x1) % p, p)) % p
    x3 = (s * s - x1 - x2) % p
    y3 = (s * (x1 - x3) - y1) % p
    
    return x3, y3

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    pub_x = int(data['public_key']['x'], 16)
    pub_y = int(data['public_key']['y'], 16)
    signatures = data['signatures']
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    a = 0
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    
    # Parse signatures
    sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sigs.append((r, s, z))
    
    # Check for nonce reuse (duplicate r values)
    r_values = [sig[0] for sig in sigs]
    r_counts = Counter(r_values)
    
    duplicates = {r: count for r, count in r_counts.items() if count > 1}
    
    if duplicates:
        # Found nonce reuse - attempt to recover private key
        for r_dup in duplicates:
            # Find two signatures with this r value
            matching_sigs = [sig for sig in sigs if sig[0] == r_dup]
            r, s1, z1 = matching_sigs[0]
            _, s2, z2 = matching_sigs[1]
            
            d = recover_private_key_from_nonce_reuse(r, s1, z1, s2, z2, n)
            
            if d:
                # Verify by computing public key
                calc_x, calc_y = point_multiply(Gx, Gy, d, p, a, n)
                
                if calc_x == pub_x and calc_y == pub_y:
                    print(json.dumps({"status": "UNDERDETERMINED", "reason": "nonce reuse detected but analysis incomplete"}))
                    return
    
    print(json.dumps({"status": "UNDERDETERMINED", "reason": "no obvious vulnerability detected"}))

if __name__ == "__main__":
    main()