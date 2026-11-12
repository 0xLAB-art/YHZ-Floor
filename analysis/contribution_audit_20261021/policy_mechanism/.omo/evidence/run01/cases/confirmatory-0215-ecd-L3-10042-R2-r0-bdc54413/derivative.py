import sys
import json
import base64


def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm."""
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

def recover_private_key(r, s1, z1, s2, z2, n):
    """Recover private key from two signatures with same r (nonce reuse)."""
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None
    
    k = (numerator * modinv(denominator, n)) % n
    
    # d = (s * k - z) / r mod n
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return d, k

def bytes_to_int(b):
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    """Convert integer to 64-character lowercase hex string."""
    hex_str = hex(n)[2:]
    return hex_str.zfill(64)

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # Find duplicate r values
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find nonce reuse and recover private key
    d = None
    k = None
    
    for r, sigs in r_map.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            _, s1, z1 = sigs[0]
            _, s2, z2 = sigs[1]
            
            result = recover_private_key(r, s1, z1, s2, z2, n)
            if result:
                d, k = result
                break
    
    # Output result
    result = {
        "d": int_to_hex(d),
        "k": int_to_hex(k)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
