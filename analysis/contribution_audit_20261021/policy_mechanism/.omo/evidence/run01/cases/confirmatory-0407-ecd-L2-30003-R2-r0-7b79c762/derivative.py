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
    """Extended Euclidean Algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode public key
    x_bytes = base64.b64decode(instance['public_key']['x'])
    y_bytes = base64.b64decode(instance['public_key']['y'])
    x = int.from_bytes(x_bytes, 'big')
    y = int.from_bytes(y_bytes, 'big')
    
    # NIST P-256 parameters
    p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
    n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
    
    # Decode signatures
    sigs = []
    for sig in instance['signatures']:
        r = int.from_bytes(base64.b64decode(sig['r']), 'big')
        s = int.from_bytes(base64.b64decode(sig['s']), 'big')
        z = int.from_bytes(base64.b64decode(sig['z']), 'big')
        sigs.append((r, s, z))
    
    # Look for repeated r values (nonce reuse)
    for i in range(len(sigs)):
        for j in range(i + 1, len(sigs)):
            r1, s1, z1 = sigs[i]
            r2, s2, z2 = sigs[j]
            
            if r1 == r2:
                # Nonce reuse detected! We can recover the private key.
                # k = (z1 - z2) / (s1 - s2) mod n
                # d = (s1 * k - z1) / r1 mod n
                
                s_diff = (s1 - s2) % n
                z_diff = (z1 - z2) % n
                
                try:
                    s_diff_inv = modinv(s_diff, n)
                    k = (z_diff * s_diff_inv) % n
                    
                    # Now recover private key d
                    r_inv = modinv(r1, n)
                    d = (r_inv * (s1 * k - z1)) % n
                    
                    # Format as 64 lowercase hex characters
                    d_hex = format(d, '064x')
                    
                    result = {"d": d_hex}
                    print(json.dumps(result))
                    return
                except ValueError:
                    continue
    
    # Should not reach here if nonce reuse exists
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()
