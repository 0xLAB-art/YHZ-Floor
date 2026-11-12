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

def bytes_to_int(b):
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n, length=64):
    """Convert integer to hex string of specified length."""
    return format(n, f'0{length}x')

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
    
    # ECDSA parameters for secp256k1 (common curve)
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Attack: Two signatures with same r but different s and z
    # This allows recovery of private key d
    r1, s1, z1 = sigs[0]
    r2, s2, z2 = sigs[1]
    
    if r1 == r2:
        # Same r, different s and z
        # From ECDSA: s = k^-1 * (z + r*d) mod n
        # s1 = k^-1 * (z1 + r*d) mod n
        # s2 = k^-1 * (z2 + r*d) mod n
        # s1 - s2 = k^-1 * (z1 - z2) mod n
        # k = (z1 - z2) / (s1 - s2) mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        # Compute k
        k = (z_diff * modinv(s_diff, n)) % n
        
        # Now recover d from first signature
        # s1 = k^-1 * (z1 + r*d) mod n
        # s1 * k = z1 + r*d mod n
        # d = (s1*k - z1) / r mod n
        
        d = ((s1 * k - z1) * modinv(r1, n)) % n
        
        # Output result
        result = {"d": int_to_hex(d, 64)}
        print(json.dumps(result))

if __name__ == "__main__":
    main()