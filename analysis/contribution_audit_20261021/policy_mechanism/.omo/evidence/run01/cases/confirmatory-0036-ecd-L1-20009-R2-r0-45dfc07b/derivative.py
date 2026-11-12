import json
import sys
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

def decode_base64_int(s):
    """Decode base64 string to integer."""
    return int.from_bytes(base64.b64decode(s), 'big')

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # Decode public key
    x = decode_base64_int(data['public_key']['x'])
    y = decode_base64_int(data['public_key']['y'])
    
    # Decode signatures
    sig1 = data['signatures'][0]
    r1 = decode_base64_int(sig1['r'])
    s1 = decode_base64_int(sig1['s'])
    z1 = decode_base64_int(sig1['z'])
    
    sig2 = data['signatures'][1]
    r2 = decode_base64_int(sig2['r'])
    s2 = decode_base64_int(sig2['s'])
    z2 = decode_base64_int(sig2['z'])
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Both signatures share the same r value (nonce reuse vulnerability)
    # ECDSA: s = k^-1 * (z + r*d) mod n
    # s1 = k^-1 * (z1 + r*d) mod n
    # s2 = k^-1 * (z2 + r*d) mod n
    # 
    # From these equations:
    # k = (z1 - z2) / (s1 - s2) mod n
    # d = (s*k - z) / r mod n
    
    # Calculate k (the nonce)
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d (the private key)
    r_inv = modinv(r1, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
