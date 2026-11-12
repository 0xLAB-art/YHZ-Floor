import sys
import json
import base64

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

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    x_bytes = base64.b64decode(instance['public_key']['x'])
    y_bytes = base64.b64decode(instance['public_key']['y'])
    
    # Parse signatures
    sigs = []
    for sig in instance['signatures']:
        r = int.from_bytes(base64.b64decode(sig['r']), 'big')
        s = int.from_bytes(base64.b64decode(sig['s']), 'big')
        z = int.from_bytes(base64.b64decode(sig['z']), 'big')
        sigs.append((r, s, z))
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Attack: two signatures with same r (nonce reuse)
    r1, s1, z1 = sigs[0]
    r2, s2, z2 = sigs[1]
    
    if r1 == r2:
        # Same nonce k used for both signatures
        # s1 = k^-1 * (z1 + r1 * d) mod n
        # s2 = k^-1 * (z2 + r2 * d) mod n
        # s1 - s2 = k^-1 * (z1 - z2) mod n
        # k = (z1 - z2) / (s1 - s2) mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        k = (z_diff * modinv(s_diff, n)) % n
        
        # Now recover d from first signature
        # s1 = k^-1 * (z1 + r1 * d) mod n
        # s1 * k = z1 + r1 * d mod n
        # d = (s1 * k - z1) / r1 mod n
        
        d = ((s1 * k - z1) * modinv(r1, n)) % n
        
        # Output result
        d_hex = format(d, '064x')
        result = {"d": d_hex}
        print(json.dumps(result))
    
if __name__ == '__main__':
    main()
