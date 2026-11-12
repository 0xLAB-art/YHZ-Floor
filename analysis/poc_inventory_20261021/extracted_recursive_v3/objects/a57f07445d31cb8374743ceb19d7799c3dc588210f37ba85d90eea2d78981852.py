import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(sig1, sig2, p):
    """
    Recover private key from two signatures with the same r value (nonce reuse).
    
    ECDSA signature equations:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    From these:
    s1 - s2 = k^-1 * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1*k - z1) / r mod n
    """
    r1 = sig1['r']
    s1 = sig1['s']
    z1 = sig1['z']
    
    r2 = sig2['r']
    s2 = sig2['s']
    z2 = sig2['z']
    
    # Verify same r value (nonce reuse vulnerability)
    if r1 != r2:
        return None
    
    r = r1
    
    # secp256k1 curve order
    n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
    
    # Calculate k (the reused nonce)
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    
    s_diff_inv = modinv(s_diff, n)
    if s_diff_inv is None:
        return None
    
    k = (z_diff * s_diff_inv) % n
    
    # Calculate private key d
    r_inv = modinv(r, n)
    if r_inv is None:
        return None
    
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse signatures
    sigs = []
    for sig in instance['signatures']:
        sigs.append({
            'r': int(sig['r'], 16),
            's': int(sig['s'], 16),
            'z': int(sig['z'], 16)
        })
    
    # secp256k1 curve order
    n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
    
    # Recover private key from the two signatures with same r
    d = recover_private_key(sigs[0], sigs[1], n)
    
    if d is None:
        # Fallback: shouldn't happen with valid input
        d = 0
    
    # Format as 64 character hex string
    d_hex = format(d, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()