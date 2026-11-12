import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
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

def recover_private_key(signatures, public_key, p, n, G):
    """
    Recover private key from ECDSA signatures with nonce reuse.
    """
    # Look for signature pairs with the same r value (indicating nonce reuse)
    r_to_sigs = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((s, z, i))
    
    # Find pairs with same r
    for r, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            # Use first two signatures with same r
            s1, z1, _ = sig_list[0]
            s2, z2, _ = sig_list[1]
            
            # Recover nonce k: k = (z1 - z2) / (s1 - s2) mod n
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            try:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Recover private key d: d = (s * k - z) / r mod n
                r_inv = modinv(r, n)
                d = ((s1 * k - z1) * r_inv) % n
                
                # Verify the private key
                Gx, Gy = G
                Qx_expected = int(public_key['x'], 16)
                Qy_expected = int(public_key['y'], 16)
                
                # Compute d * G and check if it matches public key
                Qx, Qy = point_multiply(d, Gx, Gy, p, n)
                
                if Qx == Qx_expected and Qy == Qy_expected:
                    return d
            except (ValueError, ZeroDivisionError):
                continue
    
    return None

def point_multiply(k, Gx, Gy, p, n):
    """Scalar multiplication on elliptic curve using double-and-add."""
    if k == 0:
        return None, None
    
    k = k % n
    result = None
    addend = (Gx, Gy)
    
    while k:
        if k & 1:
            result = point_add(result, addend, p)
        addend = point_add(addend, addend, p)
        k >>= 1
    
    return result

def point_add(P, Q, p):
    """Add two points on elliptic curve y^2 = x^3 + ax + b mod p."""
    if P is None or P[0] is None:
        return Q
    if Q is None or Q[0] is None:
        return P
    
    x1, y1 = P
    x2, y2 = Q
    
    # secp256k1 has a = 0, b = 7
    a = 0
    
    if x1 == x2:
        if y1 == y2:
            # Point doubling
            s = (3 * x1 * x1 + a) * modinv(2 * y1, p) % p
        else:
            # Points are inverses
            return None, None
    else:
        # Point addition
        s = (y2 - y1) * modinv(x2 - x1, p) % p
    
    x3 = (s * s - x1 - x2) % p
    y3 = (s * (x1 - x3) - y1) % p
    
    return x3, y3

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    public_key = instance['public_key']
    signatures = instance['signatures']
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    G = (Gx, Gy)
    
    # Recover private key
    d = recover_private_key(signatures, public_key, p, n, G)
    
    if d is None:
        # Fallback: shouldn't happen with valid input
        d = 0
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()