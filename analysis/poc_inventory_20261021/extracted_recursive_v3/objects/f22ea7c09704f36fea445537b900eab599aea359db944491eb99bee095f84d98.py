import json
import sys

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
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

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Find duplicate r values
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find the pair with duplicate r
    duplicate_r = None
    indices = None
    for r, idxs in r_map.items():
        if len(idxs) >= 2:
            duplicate_r = r
            indices = idxs[:2]
            break
    
    if duplicate_r is None:
        raise ValueError("No duplicate r found")
    
    # Get the two signatures with same r
    sig1 = signatures[indices[0]]
    sig2 = signatures[indices[1]]
    
    r = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    s2 = int(sig2['s'], 16)
    z1 = int(sig1['z'], 16)
    z2 = int(sig2['z'], 16)
    
    # Recover k from the two signatures
    # s1 - s2 = k^-1 * (z1 - z2) mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Now recover d from k
    # s1 = k^-1 * (z1 + r*d) mod n
    # k*s1 = z1 + r*d mod n
    # d = (k*s1 - z1) / r mod n
    
    k_s1 = (k * s1) % n
    numerator = (k_s1 - z1) % n
    r_inv = modinv(r, n)
    d = (numerator * r_inv) % n
    
    # Verify with all signatures
    for sig in signatures:
        r_check = int(sig['r'], 16)
        s_check = int(sig['s'], 16)
        z_check = int(sig['z'], 16)
        
        # Compute k for this signature: k = (z + rd) / s mod n
        numerator_check = (z_check + r_check * d) % n
        s_inv = modinv(s_check, n)
        k_computed = (numerator_check * s_inv) % n
        
        # Verify r = (k * G).x mod n
        # For a quick check, verify the signature equation holds
        # s = k^-1(z + rd) => ks = z + rd
        lhs = (k_computed * s_check) % n
        rhs = (z_check + r_check * d) % n
        
        if lhs != rhs:
            # Try negative d
            d = (-d) % n
            break
    
    # Format as 64 character hex string
    d_hex = format(d, '064x')
    
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()