import json
import sys

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

def recover_private_key(signatures, n):
    """
    Recover private key from ECDSA signatures with nonce reuse.
    If two signatures share the same r value, they used the same nonce k.
    """
    # Group signatures by r value
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(sig)
    
    # Find signatures with the same r (nonce reuse)
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1, sig2 = sigs[0], sigs[1]
            
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # From ECDSA: s = k^-1 * (z + r*d) mod n
            # s1 = k^-1 * (z1 + r*d) mod n
            # s2 = k^-1 * (z2 + r*d) mod n
            # s1 - s2 = k^-1 * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            s_diff_inv = modinv(s_diff, n)
            if s_diff_inv is None:
                continue
            
            k = (z_diff * s_diff_inv) % n
            
            # Now recover d: s1 = k^-1 * (z1 + r*d) mod n
            # s1 * k = z1 + r*d mod n
            # d = (s1*k - z1) / r mod n
            
            k_inv = modinv(k, n)
            if k_inv is None:
                continue
            
            r_inv = modinv(r, n)
            if r_inv is None:
                continue
            
            d = ((s1 * k - z1) * r_inv) % n
            
            return d
    
    return None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Recover private key
    d = recover_private_key(signatures, n)
    
    if d is not None:
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        result = {"d": d_hex}
        print(json.dumps(result))
    else:
        # Fallback (should not happen with valid instance)
        print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()
