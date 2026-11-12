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

def recover_private_key(public_key, signatures):
    """
    Recover ECDSA private key from two signatures with the same r but different messages.
    """
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode public key
    x = int.from_bytes(base64.b64decode(public_key['x']), 'big')
    y = int.from_bytes(base64.b64decode(public_key['y']), 'big')
    
    # Decode signatures
    sig1 = signatures[0]
    sig2 = signatures[1]
    
    r = int.from_bytes(base64.b64decode(sig1['r']), 'big')
    s1 = int.from_bytes(base64.b64decode(sig1['s']), 'big')
    s2 = int.from_bytes(base64.b64decode(sig2['s']), 'big')
    z1 = int.from_bytes(base64.b64decode(sig1['z']), 'big')
    z2 = int.from_bytes(base64.b64decode(sig2['z']), 'big')
    
    # Verify r is the same
    r2 = int.from_bytes(base64.b64decode(sig2['r']), 'big')
    assert r == r2, "r values must be the same"
    
    # Recover k (nonce) using: k = (z1 - z2) / (s1 - s2) mod n
    # From ECDSA: s = k^-1 * (z + r*d) mod n
    # s1 = k^-1 * (z1 + r*d) mod n
    # s2 = k^-1 * (z2 + r*d) mod n
    # s1 - s2 = k^-1 * (z1 - z2) mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    
    delta_s = (s1 - s2) % n
    delta_z = (z1 - z2) % n
    
    k = (delta_z * modinv(delta_s, n)) % n
    
    # Recover d (private key) using: d = (s*k - z) / r mod n
    # From s = k^-1 * (z + r*d), we get: s*k = z + r*d
    # Therefore: d = (s*k - z) / r mod n
    
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    # Convert to hex
    d_hex = format(d, '064x')
    
    return d_hex

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Extract data
    public_key = instance['public_key']
    signatures = instance['signatures']
    
    # Recover private key
    d_hex = recover_private_key(public_key, signatures)
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
