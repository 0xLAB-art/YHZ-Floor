import sys
import json
import base64

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

def modinv(a, m):
    """Modular multiplicative inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(r, s1, s2, z1, z2, n):
    """Recover private key from two signatures with the same r value (nonce reuse)"""
    # k = (z1 - z2) / (s1 - s2) mod n
    # d = (s*k - z) / r mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    if s_diff_inv is None:
        return None, None
    
    k = (z_diff * s_diff_inv) % n
    
    # Now recover d using d = (s*k - z) / r mod n
    r_inv = modinv(r, n)
    if r_inv is None:
        return None, None
    
    d = ((s1 * k - z1) * r_inv) % n
    
    return d, k

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
        if r in r_map:
            r_map[r].append((i, s, z))
        else:
            r_map[r] = [(i, s, z)]
    
    # Find a pair with duplicate r
    d = None
    k = None
    
    for r, sigs in r_map.items():
        if len(sigs) >= 2:
            # Use first two signatures with this r
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            d, k = recover_private_key(r, s1, s2, z1, z2, n)
            if d is not None:
                break
    
    # Output result
    result = {
        "d": int_to_hex(d),
        "k": int_to_hex(k)
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()