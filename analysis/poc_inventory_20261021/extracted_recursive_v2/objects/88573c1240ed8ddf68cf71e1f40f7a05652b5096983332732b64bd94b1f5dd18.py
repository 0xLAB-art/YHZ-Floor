import sys
import json
import base64

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

def decode_base64_to_int(b64_str):
    """Decode base64 string to integer."""
    decoded = base64.b64decode(b64_str)
    return int.from_bytes(decoded, byteorder='big')

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    pub_x = decode_base64_to_int(instance['public_key']['x'])
    pub_y = decode_base64_to_int(instance['public_key']['y'])
    
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
        # Nonce reuse: k = (z1 - z2) / (s1 - s2) mod n
        # Private key: d = (s1 * k - z1) / r1 mod n
        
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        k = (numerator * modinv(denominator, n)) % n
        
        # Calculate private key
        numerator_d = (s1 * k - z1) % n
        denominator_d = r1 % n
        d = (numerator_d * modinv(denominator_d, n)) % n
        
        # Format as 64 hex characters
        d_hex = format(d, '064x')
        
        result = {"d": d_hex}
        print(json.dumps(result))

if __name__ == "__main__":
    main()
