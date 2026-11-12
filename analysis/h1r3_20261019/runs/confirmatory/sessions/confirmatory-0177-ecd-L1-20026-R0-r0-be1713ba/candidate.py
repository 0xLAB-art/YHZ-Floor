import json
import sys

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
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

def recover_private_key(sig1, sig2, n):
    """Recover private key from two signatures with same r (nonce reuse)."""
    r = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # From s1 = k^-1(z1 + rd) and s2 = k^-1(z2 + rd)
    # We get: s1 - s2 = k^-1(z1 - z2)
    # So: k = (z1 - z2) / (s1 - s2) mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    # k = z_diff * modinv(s_diff, n) mod n
    k = (z_diff * modinv(s_diff, n)) % n
    
    # Now recover d from: s1 = k^-1(z1 + rd)
    # s1 * k = z1 + rd
    # rd = s1 * k - z1
    # d = (s1 * k - z1) / r mod n
    
    k_inv = modinv(k, n)
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    sig1 = instance['signatures'][0]
    sig2 = instance['signatures'][1]
    
    # Recover private key
    d = recover_private_key(sig1, sig2, n)
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
