import sys
import json
from collections import defaultdict

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n):
    """
    Recover private key k (nonce) and d when same nonce is used twice.
    r = same for both signatures
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    r_inv = modinv(r, n)
    d = (((s1 * k - z1) % n) * r_inv) % n
    
    return d, k

def main():
    # ECDSA curve parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # Group signatures by r value to find nonce reuse
    r_groups = defaultdict(list)
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        r_groups[r].append((s, z))
    
    # Find r values that appear more than once (nonce reuse)
    for r, sig_list in r_groups.items():
        if len(sig_list) >= 2:
            # Use first two signatures with same r
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            try:
                d, k = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
                
                # Format as 64 lowercase hex characters
                d_hex = format(d, '064x')
                k_hex = format(k, '064x')
                
                result = {
                    "d": d_hex,
                    "k": k_hex
                }
                
                print(json.dumps(result))
                return
            except:
                continue
    
    # Should not reach here if instance is valid
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()