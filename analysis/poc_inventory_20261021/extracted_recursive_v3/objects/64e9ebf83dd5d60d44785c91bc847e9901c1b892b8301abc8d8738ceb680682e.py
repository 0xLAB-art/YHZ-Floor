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
    """Extended Euclidean Algorithm."""
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
    """Convert integer to 64-character hex string."""
    h = hex(n)[2:].rstrip('L')
    return h.zfill(64)

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
    y = bytes_to_int(base64.b64decode(instance['public_key']['y']))
    
    # Parse signatures
    sigs = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        sigs.append({'r': r, 's': s, 'z': z})
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Attack: two signatures with same r but different s, z
    # This reveals the nonce k and then the private key d
    sig1 = sigs[0]
    sig2 = sigs[1]
    
    r = sig1['r']
    s1 = sig1['s']
    z1 = sig1['z']
    s2 = sig2['s']
    z2 = sig2['z']
    
    # From ECDSA: s = k^(-1) * (z + r*d) mod n
    # s1 = k^(-1) * (z1 + r*d) mod n
    # s2 = k^(-1) * (z2 + r*d) mod n
    # s1 - s2 = k^(-1) * (z1 - z2) mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    
    k = (z_diff * modinv(s_diff, n)) % n
    
    # Now recover d from: s1 = k^(-1) * (z1 + r*d) mod n
    # s1 * k = z1 + r*d mod n
    # d = (s1*k - z1) / r mod n
    
    d = ((s1 * k - z1) % n * modinv(r, n)) % n
    
    # Output result
    result = {"d": int_to_hex(d)}
    print(json.dumps(result))

if __name__ == "__main__":
    main()