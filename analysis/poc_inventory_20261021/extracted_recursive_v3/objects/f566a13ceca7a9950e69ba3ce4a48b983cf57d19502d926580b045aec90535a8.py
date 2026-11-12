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

def recover_private_key(signatures, public_key, p, n):
    """
    Recover private key from ECDSA signatures with repeated nonce.
    """
    # Look for signatures with the same r value (indicating same k)
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(sig)
    
    # Find a pair with same r
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            sig1, sig2 = sigs[0], sigs[1]
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Calculate k: k = (z1 - z2) / (s1 - s2) mod n
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
            
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Calculate private key: d = (s*k - z) / r mod n
            d = ((s1 * k - z1) % n * modinv(r, n)) % n
            
            # Verify with public key
            Gx, Gy = get_generator()
            Px, Py = scalar_mult(d, Gx, Gy, p)
            
            pub_x = int(public_key['x'], 16)
            pub_y = int(public_key['y'], 16)
            
            if Px == pub_x and Py == pub_y:
                return d
            
            # Try negative k
            k = n - k
            d = ((s1 * k - z1) % n * modinv(r, n)) % n
            Px, Py = scalar_mult(d, Gx, Gy, p)
            
            if Px == pub_x and Py == pub_y:
                return d
    
    return None

def get_generator():
    """Return secp256k1 generator point."""
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    return Gx, Gy

def scalar_mult(k, x, y, p):
    """Scalar multiplication on elliptic curve using double-and-add."""
    a = 0
    if k == 0:
        return None, None
    
    result_x, result_y = None, None
    addend_x, addend_y = x, y
    
    while k:
        if k & 1:
            if result_x is None:
                result_x, result_y = addend_x, addend_y
            else:
                result_x, result_y = point_add(result_x, result_y, addend_x, addend_y, p, a)
        addend_x, addend_y = point_add(addend_x, addend_y, addend_x, addend_y, p, a)
        k >>= 1
    
    return result_x, result_y

def point_add(x1, y1, x2, y2, p, a):
    """Add two points on an elliptic curve."""
    if x1 == x2 and y1 == y2:
        # Point doubling
        s = (3 * x1 * x1 + a) % p
        s = (s * modinv(2 * y1, p)) % p
    else:
        # Point addition
        s = (y2 - y1) % p
        s = (s * modinv((x2 - x1) % p, p)) % p
    
    x3 = (s * s - x1 - x2) % p
    y3 = (s * (x1 - x3) - y1) % p
    
    return x3, y3

def main():
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    public_key = data['public_key']
    
    d = recover_private_key(signatures, public_key, p, n)
    
    if d is None:
        d = 0
    
    result = {"d": format(d, '064x')}
    print(json.dumps(result))

if __name__ == "__main__":
    main()