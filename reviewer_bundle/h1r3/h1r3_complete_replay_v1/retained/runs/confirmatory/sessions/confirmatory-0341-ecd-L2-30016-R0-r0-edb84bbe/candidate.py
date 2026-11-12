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

def recover_private_key(signatures, n, public_key_x, public_key_y):
    """
    Recover private key from ECDSA signatures with repeated nonce (r value).
    
    For two signatures with the same r but different s and z:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    Subtracting: s1 - s2 = k^-1 * (z1 - z2) mod n
    Therefore: k = (z1 - z2) / (s1 - s2) mod n
    And: d = (s*k - z) / r mod n
    """
    
    # Group signatures by r value
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append((s, z))
    
    # Find r values that appear more than once
    for r, sig_list in r_groups.items():
        if len(sig_list) >= 2:
            # Use first two signatures with this r
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            # Calculate k: k = (z1 - z2) / (s1 - s2) mod n
            z_diff = (z1 - z2) % n
            s_diff = (s1 - s2) % n
            
            try:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Calculate d: d = (s*k - z) / r mod n
                r_inv = modinv(r, n)
                d = ((s1 * k - z1) * r_inv) % n
                
                return d
            except ValueError:
                continue
    
    return None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    public_key = instance['public_key']
    signatures = instance['signatures']
    
    public_key_x = int(public_key['x'], 16)
    public_key_y = int(public_key['y'], 16)
    
    # Recover private key
    d = recover_private_key(signatures, n, public_key_x, public_key_y)
    
    if d is None:
        # Fallback: should not happen with the given instance
        d = 0
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
