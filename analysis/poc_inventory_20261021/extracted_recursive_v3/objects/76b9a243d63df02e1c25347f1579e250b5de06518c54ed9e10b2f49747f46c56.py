import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
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

def recover_private_key(public_key, sig1, sig2):
    """
    Recover private key from two signatures with the same r value (nonce reuse).
    
    Given two ECDSA signatures with the same r:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    We can solve for k and then d.
    """
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    r = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    s2 = int(sig2['s'], 16)
    z1 = int(sig1['z'], 16)
    z2 = int(sig2['z'], 16)
    
    # From the two equations:
    # s1 - s2 = k^(-1) * (z1 - z2) mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    
    ds = (s1 - s2) % n
    dz = (z1 - z2) % n
    
    k = (dz * modinv(ds, n)) % n
    
    # Now recover d from: s1 = k^(-1) * (z1 + r*d) mod n
    # s1 * k = z1 + r*d mod n
    # d = (s1*k - z1) / r mod n
    
    d = ((s1 * k - z1) % n * modinv(r, n)) % n
    
    return d

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    public_key = instance['public_key']
    signatures = instance['signatures']
    
    # Check if we have nonce reuse (same r value)
    sig1 = signatures[0]
    sig2 = signatures[1]
    
    if sig1['r'] == sig2['r']:
        # Nonce reuse attack
        d = recover_private_key(public_key, sig1, sig2)
        d_hex = format(d, '064x')
        print(json.dumps({"d": d_hex}))
    else:
        # Should not happen based on the instance, but handle gracefully
        print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()