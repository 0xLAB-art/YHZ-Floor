import sys
import json

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

def recover_private_key(sig1, sig2, n):
    """
    Recover private key from two signatures with the same r value.
    
    ECDSA signing: s = k^(-1) * (z + r*d) mod n
    Rearranging: k = (z + r*d) / s mod n
    
    With two signatures sharing the same k (same r):
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    Therefore:
    s1 - s2 = k^(-1) * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    
    Once we have k:
    d = (s*k - z) / r mod n
    """
    r = sig1['r']
    s1 = sig1['s']
    z1 = sig1['z']
    s2 = sig2['s']
    z2 = sig2['z']
    
    # Compute k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # Compute d = (s*k - z) / r mod n
    numerator = (s1 * k - z1) % n
    d = (numerator * modinv(r, n)) % n
    
    return d

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    sigs = []
    for sig in instance['signatures']:
        sigs.append({
            'r': int(sig['r'], 16),
            's': int(sig['s'], 16),
            'z': int(sig['z'], 16)
        })
    
    # Check if signatures share the same r value (nonce reuse attack)
    if sigs[0]['r'] == sigs[1]['r']:
        d = recover_private_key(sigs[0], sigs[1], n)
    else:
        raise ValueError("Signatures do not share the same r value")
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()