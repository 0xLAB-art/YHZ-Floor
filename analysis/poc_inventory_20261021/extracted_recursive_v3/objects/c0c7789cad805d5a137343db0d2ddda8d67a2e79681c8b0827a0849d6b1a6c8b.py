import json
import sys

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

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    Qx = int(instance['public_key']['x'], 16)
    Qy = int(instance['public_key']['y'], 16)
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # Look for repeated r values (nonce reuse)
    r_dict = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_dict:
            r_dict[r] = []
        r_dict[r].append((i, s, z))
    
    # Find a pair with the same r
    private_key = None
    k_value = None
    
    for r, sigs in r_dict.items():
        if len(sigs) >= 2:
            # We have nonce reuse!
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            # From ECDSA: s = k^-1 * (z + r*d) mod n
            # s1 = k^-1 * (z1 + r*d) mod n
            # s2 = k^-1 * (z2 + r*d) mod n
            # s1 - s2 = k^-1 * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
            
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Now recover private key d
            # s1 = k^-1 * (z1 + r*d) mod n
            # s1 * k = z1 + r*d mod n
            # d = (s1*k - z1) / r mod n
            
            if r == 0:
                continue
            
            r_inv = modinv(r, n)
            d = ((s1 * k - z1) * r_inv) % n
            
            # Verify this is correct by checking the public key
            # In ECDSA, Q = d*G where G is the generator point
            # We can verify by checking one of the signatures
            
            # Verify: Check if this d works for signature verification
            # We'll just use it directly since the problem asks for d and k
            
            private_key = d
            k_value = k
            break
    
    # Format output
    result = {
        "d": format(private_key, '064x'),
        "k": format(k_value, '064x')
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()