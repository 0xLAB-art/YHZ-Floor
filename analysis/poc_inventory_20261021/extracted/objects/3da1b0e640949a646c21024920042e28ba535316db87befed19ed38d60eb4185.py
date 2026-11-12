import sys
import json
from collections import defaultdict

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        return None
    return (x % m + m) % m

def recover_private_key(sig1, sig2, n):
    """
    Recover private key from two signatures with the same r value (same k).
    
    Given:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    We can solve for k and then d.
    """
    r1, s1, z1 = sig1['r'], sig1['s'], sig1['z']
    r2, s2, z2 = sig2['r'], sig2['s'], sig2['z']
    
    # Convert hex to int
    r = int(r1, 16)
    s1_int = int(s1, 16)
    s2_int = int(s2, 16)
    z1_int = int(z1, 16)
    z2_int = int(z2, 16)
    
    # From s1 - s2 = k^-1 * (z1 - z2) mod n
    # Therefore k = (z1 - z2) / (s1 - s2) mod n
    s_diff = (s1_int - s2_int) % n
    z_diff = (z1_int - z2_int) % n
    
    s_diff_inv = modinv(s_diff, n)
    if s_diff_inv is None:
        return None
    
    k = (z_diff * s_diff_inv) % n
    
    # Now recover d from s1 = k^-1 * (z1 + r*d) mod n
    # k * s1 = z1 + r*d mod n
    # d = (k*s1 - z1) / r mod n
    k_inv = modinv(k, n)
    if k_inv is None:
        return None
    
    r_inv = modinv(r, n)
    if r_inv is None:
        return None
    
    d = ((k * s1_int - z1_int) * r_inv) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Group signatures by r value
    r_groups = defaultdict(list)
    for sig in signatures:
        r_groups[sig['r']].append(sig)
    
    # Find groups with repeated r values
    for r_value, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Try to recover private key from first two signatures with same r
            d = recover_private_key(sigs[0], sigs[1], n)
            if d is not None:
                # Format as 64 lowercase hex characters
                d_hex = format(d, '064x')
                result = {"d": d_hex}
                print(json.dumps(result))
                return
    
    # If no repeated r found, output error (shouldn't happen with valid input)
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()
