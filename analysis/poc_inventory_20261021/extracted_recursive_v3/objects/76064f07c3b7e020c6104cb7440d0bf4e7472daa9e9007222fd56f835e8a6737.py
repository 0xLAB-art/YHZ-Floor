import sys
import json
import hashlib

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
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

def recover_key_from_nonce_reuse(r, s1, s2, z1, z2, n):
    """Recover private key d and nonce k from two signatures with same nonce"""
    # k = (z1 - z2) / (s1 - s2) mod n
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    if s_diff_inv is None:
        return None, None
    
    k = (z_diff * s_diff_inv) % n
    
    # d = (s*k - z) / r mod n
    r_inv = modinv(r, n)
    if r_inv is None:
        return None, None
    
    d = (((s1 * k - z1) % n) * r_inv) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find signatures with same r value
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find repeated r
    d = None
    k = None
    
    for r, sigs in r_map.items():
        if len(sigs) >= 2:
            # Use first two signatures with this r
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            d, k = recover_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
            
            if d is not None and k is not None:
                break
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()