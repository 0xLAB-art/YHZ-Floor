import json
import sys
import hashlib

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def base64_to_int(s):
    """Convert base64 string to integer."""
    import base64
    return int.from_bytes(base64.b64decode(s), 'big')

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # Parse public key
    x = base64_to_int(data['public_key']['x'])
    y = base64_to_int(data['public_key']['y'])
    
    # Parse signatures
    sig1 = data['signatures'][0]
    sig2 = data['signatures'][1]
    
    r1 = base64_to_int(sig1['r'])
    s1 = base64_to_int(sig1['s'])
    z1 = base64_to_int(sig1['z'])
    
    r2 = base64_to_int(sig2['r'])
    s2 = base64_to_int(sig2['s'])
    z2 = base64_to_int(sig2['z'])
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # ECDSA nonce reuse attack
    # If r1 == r2, then the same nonce k was used
    # s1 = k^-1 * (z1 + r1 * d) mod n
    # s2 = k^-1 * (z2 + r2 * d) mod n
    # where d is the private key
    
    if r1 == r2:
        # s1 - s2 = k^-1 * (z1 - z2) mod n
        # k = (z1 - z2) / (s1 - s2) mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        k = (z_diff * modinv(s_diff, n)) % n
        
        # Now recover d from: s1 = k^-1 * (z1 + r1 * d) mod n
        # s1 * k = z1 + r1 * d mod n
        # d = (s1 * k - z1) / r1 mod n
        
        d = ((s1 * k - z1) % n * modinv(r1, n)) % n
        
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        
        result = {"d": d_hex}
        print(json.dumps(result))

if __name__ == '__main__':
    main()