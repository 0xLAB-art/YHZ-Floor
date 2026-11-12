import json
import sys

def mod_inverse(a, m):
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

def recover_private_key(r, s1, s2, z1, z2, n):
    """
    Recover private key from two signatures with same r value (nonce reuse).
    
    Given:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    We can derive:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    # Calculate k from the two signatures
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    k = (numerator * mod_inverse(denominator, n)) % n
    
    # Calculate d (private key) using the first signature
    d = (((s1 * k) % n - z1) % n * mod_inverse(r, n)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Extract signatures
    sig1 = instance['signatures'][0]
    sig2 = instance['signatures'][1]
    
    r1 = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    
    r2 = int(sig2['r'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Check if both signatures have the same r value (nonce reuse vulnerability)
    if r1 == r2:
        # Recover private key
        d = recover_private_key(r1, s1, s2, z1, z2, n)
        
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        
        # Output result
        result = {"d": d_hex}
        print(json.dumps(result))
    else:
        raise ValueError("Signatures do not have matching r values")

if __name__ == "__main__":
    main()
