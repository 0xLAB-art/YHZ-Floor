import json
import sys

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

def recover_key_from_nonce_reuse(r, s1, z1, s2, z2, n):
    """Recover private key from two signatures using the same nonce."""
    # Calculate k from the two signatures
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    if s_diff_inv is None:
        return None, None
    
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d from k
    r_inv = modinv(r, n)
    if r_inv is None:
        return None, None
    
    d = ((s1 * k - z1) * r_inv) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Find duplicate r values
    r_map = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((s, z))
    
    # Find a pair with the same r
    d_found = None
    k_found = None
    
    for r, sig_list in r_map.items():
        if len(sig_list) >= 2:
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            d, k = recover_key_from_nonce_reuse(r, s1, z1, s2, z2, n)
            
            if d is not None and k is not None:
                d_found = d
                k_found = k
                break
    
    # Format output
    result = {
        "d": format(d_found, '064x'),
        "k": format(k_found, '064x')
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
