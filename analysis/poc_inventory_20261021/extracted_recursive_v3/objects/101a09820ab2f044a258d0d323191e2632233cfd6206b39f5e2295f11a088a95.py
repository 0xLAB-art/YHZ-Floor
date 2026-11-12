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

def recover_private_key(sig1, sig2, n):
    """
    Recover private key from two signatures with the same r but different s and z.
    
    The ECDSA signing equation is:
    s = k^(-1) * (z + r*d) mod n
    
    Rearranging:
    s*k = z + r*d mod n
    
    For two signatures with same r (same k):
    s1*k = z1 + r*d mod n
    s2*k = z2 + r*d mod n
    
    Subtracting:
    (s1 - s2)*k = (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    
    Then we can solve for d:
    d = (s*k - z) / r mod n
    """
    r = sig1['r']
    s1 = sig1['s']
    z1 = sig1['z']
    s2 = sig2['s']
    z2 = sig2['z']
    
    # Calculate k
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d (private key)
    r_inv = modinv(r, n)
    d = (r_inv * (s1 * k - z1)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    sig1 = {
        'r': int(instance['signatures'][0]['r'], 16),
        's': int(instance['signatures'][0]['s'], 16),
        'z': int(instance['signatures'][0]['z'], 16)
    }
    
    sig2 = {
        'r': int(instance['signatures'][1]['r'], 16),
        's': int(instance['signatures'][1]['s'], 16),
        'z': int(instance['signatures'][1]['z'], 16)
    }
    
    # Check if both signatures have the same r value (reused nonce attack)
    if sig1['r'] == sig2['r']:
        d = recover_private_key(sig1, sig2, n)
        d_hex = format(d, '064x')
        print(json.dumps({"d": d_hex}))
    else:
        print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()