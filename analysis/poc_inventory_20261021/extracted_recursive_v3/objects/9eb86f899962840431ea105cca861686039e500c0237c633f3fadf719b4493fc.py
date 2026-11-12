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

def recover_private_key(signatures, n):
    """
    Recover private key from ECDSA signatures with nonce reuse.
    If two signatures share the same r value, they used the same nonce k.
    """
    # Group signatures by r value
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append({'s': s, 'z': z, 'r': r})
    
    # Find pairs with same r (nonce reuse)
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1 = sigs[0]
            sig2 = sigs[1]
            
            s1, z1 = sig1['s'], sig1['z']
            s2, z2 = sig2['s'], sig2['z']
            
            # From ECDSA: s = k^(-1) * (z + r*d) mod n
            # s1 = k^(-1) * (z1 + r*d) mod n
            # s2 = k^(-1) * (z2 + r*d) mod n
            # s1 - s2 = k^(-1) * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
            
            try:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Now recover d: s1 = k^(-1) * (z1 + r*d) mod n
                # k * s1 = z1 + r*d mod n
                # d = (k * s1 - z1) / r mod n
                
                if k == 0:
                    continue
                
                k_inv = modinv(k, n)
                # From s = k^(-1) * (z + r*d), we get: k*s = z + r*d
                # So: r*d = k*s - z
                # d = (k*s - z) / r
                
                numerator = (k * s1 - z1) % n
                if r == 0:
                    continue
                
                r_inv = modinv(r, n)
                d = (numerator * r_inv) % n
                
                return d, k
            except ValueError:
                continue
    
    return None, None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Recover private key and nonce
    d, k = recover_private_key(signatures, n)
    
    if d is None:
        # Fallback: should not happen with nonce reuse
        d = 0
        k = 0
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()