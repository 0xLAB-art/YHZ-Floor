import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find signatures with same r (indices 2 and 5, 0-indexed)
    sig1 = signatures[2]
    sig2 = signatures[5]
    
    r = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Recover k from two signatures with same r
    # k = (z1 - z2) / (s1 - s2) mod n
    k = ((z1 - z2) % n * modinv((s1 - s2) % n, n)) % n
    
    # Recover d from k
    # d = (s*k - z) / r mod n
    d = ((s1 * k - z1) % n * modinv(r, n)) % n
    
    result = {
        "d": format(d, '064x')
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
