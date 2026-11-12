import json
import sys
from collections import defaultdict
from math import gcd

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    if gcd(a, m) != 1:
        return None
    u1, u2, u3 = 1, 0, a
    v1, v2, v3 = 0, 1, m
    while v3 != 0:
        q = u3 // v3
        v1, v2, v3, u1, u2, u3 = (u1 - q * v1), (u2 - q * v2), (u3 - q * v3), v1, v2, v3
    return u1 % m

def recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n):
    """Recover private key k (nonce) and d from two signatures with same r."""
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    denom_inv = modinv(denominator, n)
    if denom_inv is None:
        return None, None
    
    k = (numerator * denom_inv) % n
    
    # d = (s * k - z) / r mod n
    k_inv = modinv(k, n)
    if k_inv is None:
        return None, None
    
    r_inv = modinv(r, n)
    if r_inv is None:
        return None, None
    
    d = (r_inv * (s1 * k - z1)) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # ECDSA curve parameters (secp256k1)
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Group signatures by r value to find nonce reuse
    r_groups = defaultdict(list)
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        r_groups[r].append((s, z))
    
    # Find r values that appear more than once (nonce reuse)
    d_found = None
    k_found = None
    
    for r, sig_list in r_groups.items():
        if len(sig_list) >= 2:
            # We have nonce reuse! Try to recover the key
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            d, k = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
            
            if d is not None and k is not None:
                d_found = d
                k_found = k
                break
    
    # Format output
    d_hex = format(d_found, '064x')
    k_hex = format(k_found, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()