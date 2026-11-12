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

def bytes_to_int(b):
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    """Convert integer to 64 lowercase hex characters."""
    return format(n, '064x')

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode public key
    x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
    y = bytes_to_int(base64.b64decode(instance['public_key']['y']))
    
    # Decode signatures
    sigs = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        sigs.append((r, s, z))
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Extract two signatures with same r
    r1, s1, z1 = sigs[0]
    r2, s2, z2 = sigs[1]
    
    # Check if r values are the same (nonce reuse attack)
    if r1 == r2:
        # Recover private key using nonce reuse
        # k = (z1 - z2) / (s1 - s2) mod n
        # d = (s1 * k - z1) / r1 mod n
        
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        k = (numerator * modinv(denominator, n)) % n
        
        # Now recover d
        d_numerator = (s1 * k - z1) % n
        d_denominator = r1 % n
        d = (d_numerator * modinv(d_denominator, n)) % n
        
        result = {"d": int_to_hex(d)}
        print(json.dumps(result))
    else:
        # Should not happen based on the instance
        print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()
