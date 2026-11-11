import sys
import json
import base64
import hashlib

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
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    x = int.from_bytes(base64.b64decode(instance['public_key']['x']), 'big')
    y = int.from_bytes(base64.b64decode(instance['public_key']['y']), 'big')
    
    # Parse signatures
    sigs = []
    for sig in instance['signatures']:
        r = int.from_bytes(base64.b64decode(sig['r']), 'big')
        s = int.from_bytes(base64.b64decode(sig['s']), 'big')
        z = int.from_bytes(base64.b64decode(sig['z']), 'big')
        sigs.append({'r': r, 's': s, 'z': z})
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Both signatures share the same r, meaning they used the same k (nonce)
    # We have: s1 = k^(-1) * (z1 + r * d) mod n
    #          s2 = k^(-1) * (z2 + r * d) mod n
    # Therefore: s1 - s2 = k^(-1) * (z1 - z2) mod n
    # So: k = (z1 - z2) / (s1 - s2) mod n
    
    r = sigs[0]['r']
    s1 = sigs[0]['s']
    z1 = sigs[0]['z']
    s2 = sigs[1]['s']
    z2 = sigs[1]['z']
    
    # Compute k
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    k = (z_diff * modinv(s_diff, n)) % n
    
    # Now recover d from: s1 = k^(-1) * (z1 + r * d) mod n
    # So: s1 * k = z1 + r * d mod n
    # Therefore: d = (s1 * k - z1) / r mod n
    
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    # Convert d to 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
