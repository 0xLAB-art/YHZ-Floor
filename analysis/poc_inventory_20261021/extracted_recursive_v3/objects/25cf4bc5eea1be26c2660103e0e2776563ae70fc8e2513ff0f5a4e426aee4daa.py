import json
import sys
from hashlib import sha256

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
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
    """Convert integer to 64-character lowercase hex string."""
    return format(n, '064x')

def base64_to_int(s):
    """Decode base64 string to integer."""
    import base64
    return bytes_to_int(base64.b64decode(s))

# ECDSA parameters for secp256k1
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    qx = base64_to_int(instance['public_key']['x'])
    qy = base64_to_int(instance['public_key']['y'])
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = base64_to_int(sig['r'])
        s = base64_to_int(sig['s'])
        z = base64_to_int(sig['z'])
        signatures.append((r, s, z))
    
    # Look for nonce reuse (same r value)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_map:
            # Found duplicate r! We can recover the private key
            j = r_map[r]
            r1, s1, z1 = signatures[j]
            r2, s2, z2 = signatures[i]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s*k - z) / r mod n
            
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            k = (numerator * modinv(denominator, n)) % n
            
            # Now compute private key d
            d = ((s1 * k - z1) * modinv(r1, n)) % n
            
            result = {
                "d": int_to_hex(d),
                "k": int_to_hex(k)
            }
            print(json.dumps(result))
            return
        else:
            r_map[r] = i
    
    # If no duplicate found, output placeholder
    result = {
        "d": int_to_hex(0),
        "k": int_to_hex(0)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()