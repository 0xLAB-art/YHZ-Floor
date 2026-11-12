import sys
import json
import base64


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

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode public key
    x = int.from_bytes(base64.b64decode(instance['public_key']['x']), 'big')
    y = int.from_bytes(base64.b64decode(instance['public_key']['y']), 'big')
    
    # Decode signatures
    sigs = []
    for sig in instance['signatures']:
        r = int.from_bytes(base64.b64decode(sig['r']), 'big')
        s = int.from_bytes(base64.b64decode(sig['s']), 'big')
        z = int.from_bytes(base64.b64decode(sig['z']), 'big')
        sigs.append((r, s, z))
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Two signatures with same r but different s and z
    r1, s1, z1 = sigs[0]
    r2, s2, z2 = sigs[1]
    
    # Verify r values are the same
    assert r1 == r2, "r values must be the same for this attack"
    
    r = r1
    
    # Recover private key using nonce reuse attack
    # s1 = k^-1 * (z1 + r*d) mod n
    # s2 = k^-1 * (z2 + r*d) mod n
    # s1 - s2 = k^-1 * (z1 - z2) mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    
    delta_s = (s1 - s2) % n
    delta_z = (z1 - z2) % n
    
    k = (delta_z * modinv(delta_s, n)) % n
    
    # Now recover d from: s1 = k^-1 * (z1 + r*d) mod n
    # k * s1 = z1 + r*d mod n
    # d = (k * s1 - z1) / r mod n
    
    d = ((k * s1 - z1) * modinv(r, n)) % n
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
