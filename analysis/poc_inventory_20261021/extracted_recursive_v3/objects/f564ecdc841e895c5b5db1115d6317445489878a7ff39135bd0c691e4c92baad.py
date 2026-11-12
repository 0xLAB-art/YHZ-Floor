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

def decode_base64_to_int(b64_str):
    """Decode base64 string to integer."""
    decoded = base64.b64decode(b64_str)
    return int.from_bytes(decoded, byteorder='big')

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    Qx = decode_base64_to_int(instance['public_key']['x'])
    Qy = decode_base64_to_int(instance['public_key']['y'])
    
    # Parse signatures
    sig1 = instance['signatures'][0]
    r1 = decode_base64_to_int(sig1['r'])
    s1 = decode_base64_to_int(sig1['s'])
    z1 = decode_base64_to_int(sig1['z'])
    
    sig2 = instance['signatures'][1]
    r2 = decode_base64_to_int(sig2['r'])
    s2 = decode_base64_to_int(sig2['s'])
    z2 = decode_base64_to_int(sig2['z'])
    
    # Check if r values are the same (nonce reuse attack)
    if r1 == r2:
        # k = (z1 - z2) / (s1 - s2) mod n
        # d = (s1 * k - z1) / r1 mod n
        
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        k = (numerator * modinv(denominator, n)) % n
        
        # Recover private key d
        numerator_d = (s1 * k - z1) % n
        d = (numerator_d * modinv(r1, n)) % n
        
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        
        print(json.dumps({"d": d_hex}))
    else:
        # Different attack needed
        print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()
