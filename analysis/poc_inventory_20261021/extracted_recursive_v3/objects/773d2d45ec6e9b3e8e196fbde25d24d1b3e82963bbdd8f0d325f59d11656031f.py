import sys
import json

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

def recover_private_key(r, s1, s2, z1, z2, n):
    """
    Recover private key from two signatures with the same r value (nonce reuse).
    
    The ECDSA signature equation is:
    s = k^(-1) * (z + r*d) mod n
    
    With two signatures using the same k:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    Rearranging:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1*k - z1) / r mod n
    """
    # Calculate k from the two signatures
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate private key d from k
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Extract signature data
    sig1 = instance['signatures'][0]
    sig2 = instance['signatures'][1]
    
    r1 = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    
    r2 = int(sig2['r'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Check if r values are the same (nonce reuse attack)
    if r1 == r2:
        d = recover_private_key(r1, s1, s2, z1, z2, n)
    else:
        raise ValueError("r values are different, cannot apply nonce reuse attack")
    
    # Format output as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
