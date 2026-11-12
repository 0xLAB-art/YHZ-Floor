import sys
import json
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

def int_to_hex(n):
    """Convert integer to 64-character lowercase hex string."""
    hex_str = format(n, '064x')
    return hex_str

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    pub_x = decode_base64_to_int(instance['public_key']['x'])
    pub_y = decode_base64_to_int(instance['public_key']['y'])
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = decode_base64_to_int(sig['r'])
        s = decode_base64_to_int(sig['s'])
        z = decode_base64_to_int(sig['z'])
        signatures.append((r, s, z))
    
    # ECDSA uses secp256k1 curve parameters
    # Order of the curve
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Look for repeated r values (nonce reuse attack)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_map:
            # Found repeated r! Can recover private key
            j = r_map[r]
            r1, s1, z1 = signatures[j]
            r2, s2, z2 = signatures[i]
            
            # Two signatures with same r (same k):
            # s1 = k^-1(z1 + r*d) mod n
            # s2 = k^-1(z2 + r*d) mod n
            # s1 - s2 = k^-1(z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            # k = z_diff / s_diff mod n
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Now recover d from: s = k^-1(z + r*d) mod n
            # s*k = z + r*d mod n
            # d = (s*k - z) / r mod n
            k_inv = modinv(k, n)
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            # Output result
            result = {
                "d": int_to_hex(d),
                "k": int_to_hex(k)
            }
            print(json.dumps(result))
            return
        else:
            r_map[r] = i
    
    # If no repeated r found, there might be another vulnerability
    # But the problem expects to find one
    raise ValueError("No nonce reuse detected")

if __name__ == "__main__":
    main()