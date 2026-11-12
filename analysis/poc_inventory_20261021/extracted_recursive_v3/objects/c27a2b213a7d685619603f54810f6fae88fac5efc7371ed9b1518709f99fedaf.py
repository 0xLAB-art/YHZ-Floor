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

def recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n):
    """
    Recover private key k (nonce) and d (private key) from two signatures
    that reused the same nonce.
    
    For ECDSA:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    From these:
    s1 - s2 = k^-1 * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    # Calculate k (the nonce)
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    
    if s_diff == 0:
        return None, None
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d (the private key)
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return k, d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA curve parameters for secp256k1
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Look for signatures with the same r value (indicating nonce reuse)
    r_map = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((s, z))
    
    # Find a pair with reused nonce
    k_result = None
    d_result = None
    
    for r, sig_list in r_map.items():
        if len(sig_list) >= 2:
            # We found nonce reuse!
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            k, d = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
            
            if k is not None and d is not None:
                k_result = k
                d_result = d
                break
    
    # Format output
    d_hex = format(d_result, '064x')
    k_hex = format(k_result, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()