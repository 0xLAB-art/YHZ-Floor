import sys
import json
import base64
import hashlib

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

def decode_base64_int(s):
    """Decode base64 string to integer."""
    b = base64.b64decode(s)
    return int.from_bytes(b, 'big')

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # Decode public key
    pub_x = decode_base64_int(data['public_key']['x'])
    pub_y = decode_base64_int(data['public_key']['y'])
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode signatures
    signatures = []
    for sig in data['signatures']:
        r = decode_base64_int(sig['r'])
        s = decode_base64_int(sig['s'])
        z = decode_base64_int(sig['z'])
        signatures.append((r, s, z))
    
    # Look for nonce reuse (same r value in different signatures)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find pairs with same r
    for r, sigs in r_map.items():
        if len(sigs) >= 2:
            # Nonce reuse detected - recover private key
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s1 * k - z1) / r mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            r_inv = modinv(r, n)
            d = (((s1 * k - z1) % n) * r_inv) % n
            
            # Format as 64 hex characters
            d_hex = format(d, '064x')
            
            print(json.dumps({"d": d_hex}))
            return
    
    # Should not reach here if there's nonce reuse
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()