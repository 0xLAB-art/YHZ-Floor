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

def recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n):
    """
    Recover private key k (nonce) and d (private key) when the same nonce
    is used for two different signatures.
    
    Given:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    We can derive:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    # Calculate k (the nonce)
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    if s_diff_inv is None:
        return None
    
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d (the private key)
    r_inv = modinv(r, n)
    if r_inv is None:
        return None
    
    d = (r_inv * (s1 * k - z1)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Look for signatures with the same r value (nonce reuse)
    r_map = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((s, z))
    
    # Find r values that appear more than once
    for r, sig_list in r_map.items():
        if len(sig_list) >= 2:
            # Try to recover the private key
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            d = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
            
            if d is not None:
                # Format as 64 lowercase hex characters
                d_hex = format(d, '064x')
                print(json.dumps({"d": d_hex}))
                return
    
    # Should not reach here if the instance is valid
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()
