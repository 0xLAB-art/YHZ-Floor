import json
import sys

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def recover_private_key(sig1, sig2):
    """Recover private key from two signatures with same r (nonce reuse)"""
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    r = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Verify r values match
    r2 = int(sig2['r'], 16)
    assert r == r2, "r values must match for nonce reuse attack"
    
    # Recover k: k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # Recover d: d = (s*k - z) / r mod n
    numerator = (s1 * k - z1) % n
    d = (numerator * modinv(r, n)) % n
    
    return d

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # Recover private key from the two signatures
    d = recover_private_key(signatures[0], signatures[1])
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output exactly one JSON object
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
