import sys
import json
import hashlib

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

def recover_key_from_duplicate_k(sig1, sig2, n):
    """
    Recover private key when two signatures share the same k (same r value).
    
    For ECDSA:
    s1 = k^-1 * (z1 + r * d) mod n
    s2 = k^-1 * (z2 + r * d) mod n
    
    From these we can derive:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1 * k - z1) / r mod n
    """
    r = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Calculate k = (z1 - z2) * (s1 - s2)^-1 mod n
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d = (s * k - z) * r^-1 mod n
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d, k

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with duplicate r values
    r_map = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find a pair with duplicate r
    d = None
    k = None
    for r_val, indices in r_map.items():
        if len(indices) >= 2:
            # Use the first two signatures with the same r
            sig1 = signatures[indices[0]]
            sig2 = signatures[indices[1]]
            d, k = recover_key_from_duplicate_k(sig1, sig2, n)
            break
    
    # Format output as 64 lowercase hex characters
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
