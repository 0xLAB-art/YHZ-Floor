import json
import sys

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

def recover_private_key(r, s1, s2, z1, z2, n):
    """Recover private key from two signatures with same nonce."""
    # k = (z1 - z2) * (s1 - s2)^-1 mod n
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # d = r^-1 * (s1 * k - z1) mod n
    r_inv = modinv(r, n)
    d = (r_inv * ((s1 * k - z1) % n)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with same r value
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find pair with same r
    for r, indices in r_map.items():
        if len(indices) >= 2:
            i, j = indices[0], indices[1]
            sig1 = signatures[i]
            sig2 = signatures[j]
            
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            d = recover_private_key(r, s1, s2, z1, z2, n)
            
            # Format as 64 lowercase hex characters
            d_hex = format(d, '064x')
            
            print(json.dumps({"d": d_hex}))
            return

if __name__ == "__main__":
    main()
