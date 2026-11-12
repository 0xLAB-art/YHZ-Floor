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

def recover_private_key(r, s1, s2, z1, z2, n):
    """
    Recover private key from two signatures with the same r value (nonce reuse).
    
    From ECDSA signature equations:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    Therefore:
    s1 - s2 = k^(-1) * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    
    Then:
    d = (s1*k - z1) / r mod n
    """
    # Calculate k from the two signatures
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate private key d
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode signatures
    sig1 = instance['signatures'][0]
    sig2 = instance['signatures'][1]
    
    r1 = int.from_bytes(base64.b64decode(sig1['r']), 'big')
    s1 = int.from_bytes(base64.b64decode(sig1['s']), 'big')
    z1 = int.from_bytes(base64.b64decode(sig1['z']), 'big')
    
    r2 = int.from_bytes(base64.b64decode(sig2['r']), 'big')
    s2 = int.from_bytes(base64.b64decode(sig2['s']), 'big')
    z2 = int.from_bytes(base64.b64decode(sig2['z']), 'big')
    
    # Check if r values are the same (nonce reuse vulnerability)
    if r1 == r2:
        d = recover_private_key(r1, s1, s2, z1, z2, n)
        result = {"d": format(d, '064x')}
        print(json.dumps(result))
    else:
        # Should not happen based on the instance
        print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()