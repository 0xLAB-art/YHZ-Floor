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

def recover_private_key(signatures, public_key, p, n):
    """
    Recover private key from ECDSA signatures with nonce reuse.
    If two signatures share the same r value, they used the same nonce k.
    """
    # Group signatures by r value
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append({'s': s, 'z': z})
    
    # Find r values with multiple signatures (nonce reuse)
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            s1, z1 = sigs[0]['s'], sigs[0]['z']
            s2, z2 = sigs[1]['s'], sigs[1]['z']
            
            # From ECDSA: s = k^(-1) * (z + r*d) mod n
            # s1 = k^(-1) * (z1 + r*d) mod n
            # s2 = k^(-1) * (z2 + r*d) mod n
            # s1 - s2 = k^(-1) * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
            
            # k = z_diff * (s_diff)^(-1) mod n
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Now recover d from: s1 = k^(-1) * (z1 + r*d) mod n
            # s1 * k = z1 + r*d mod n
            # d = (s1*k - z1) / r mod n
            
            k_inv = modinv(k, n)
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            return d
    
    return None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    public_key = instance['public_key']
    signatures = instance['signatures']
    
    # Recover private key
    d = recover_private_key(signatures, public_key, p, n)
    
    if d is None:
        # Fallback: shouldn't happen with the given data
        d = 0
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
