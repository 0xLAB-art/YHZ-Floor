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
    
    # ECDSA parameters for secp256r1 (P-256)
    p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Parse public key
    Qx = decode_base64_to_int(instance['public_key']['x'])
    Qy = decode_base64_to_int(instance['public_key']['y'])
    
    # Parse signatures
    sigs = []
    for sig in instance['signatures']:
        r = decode_base64_to_int(sig['r'])
        s = decode_base64_to_int(sig['s'])
        z = decode_base64_to_int(sig['z'])
        sigs.append((r, s, z))
    
    # Check if we have two signatures with the same r value
    if len(sigs) >= 2 and sigs[0][0] == sigs[1][0]:
        r1, s1, z1 = sigs[0]
        r2, s2, z2 = sigs[1]
        
        # Two signatures with same r means same k was used
        # s1 = k^(-1) * (z1 + r * d) mod n
        # s2 = k^(-1) * (z2 + r * d) mod n
        # s1 - s2 = k^(-1) * (z1 - z2) mod n
        # k = (z1 - z2) / (s1 - s2) mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        # k = z_diff / s_diff mod n
        s_diff_inv = modinv(s_diff, n)
        k = (z_diff * s_diff_inv) % n
        
        # Now recover d from: s = k^(-1) * (z + r * d) mod n
        # s * k = z + r * d mod n
        # d = (s * k - z) / r mod n
        
        k_inv = modinv(k, n)
        
        # Use first signature to recover d
        # s1 = k^(-1) * (z1 + r1 * d) mod n
        # k = (z1 + r1 * d) / s1 mod n
        # Alternatively: d = (s * k - z) / r mod n
        
        d = ((s1 * k - z1) * modinv(r1, n)) % n
        
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        
        result = {"d": d_hex}
        print(json.dumps(result))

if __name__ == "__main__":
    main()
