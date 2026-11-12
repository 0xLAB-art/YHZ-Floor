import sys
import json

def mod_inverse(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
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
    
    # Parse public key
    pub_x = int(instance['public_key']['x'], 16)
    pub_y = int(instance['public_key']['y'], 16)
    
    # Parse signatures
    sig1 = instance['signatures'][0]
    sig2 = instance['signatures'][1]
    
    r1 = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    
    r2 = int(sig2['r'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Both signatures share the same r value, indicating same nonce k
    # ECDSA signature: r = (k * G).x mod n, s = k^-1 * (z + r * d) mod n
    # From two signatures with same r (same k):
    # s1 = k^-1 * (z1 + r * d) mod n
    # s2 = k^-1 * (z2 + r * d) mod n
    # s1 - s2 = k^-1 * (z1 - z2) mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    
    if r1 == r2:
        # Same nonce attack
        z_diff = (z1 - z2) % n
        s_diff = (s1 - s2) % n
        
        # k = (z1 - z2) / (s1 - s2) mod n
        s_diff_inv = mod_inverse(s_diff, n)
        k = (z_diff * s_diff_inv) % n
        
        # Now recover private key d from first signature
        # s1 = k^-1 * (z1 + r1 * d) mod n
        # s1 * k = z1 + r1 * d mod n
        # d = (s1 * k - z1) / r1 mod n
        
        r1_inv = mod_inverse(r1, n)
        d = ((s1 * k - z1) % n * r1_inv) % n
        
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        
        # Output
        result = {"d": d_hex}
        print(json.dumps(result))
    else:
        # Different r values - shouldn't happen based on the instance
        pass

if __name__ == '__main__':
    main()
