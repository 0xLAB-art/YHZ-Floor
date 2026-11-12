import sys
import json

def mod_inverse(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def solve_ecdsa_nonce_reuse(r, s1, s2, z1, z2, n):
    """Recover private key from nonce reuse"""
    # k = (z1 - z2) / (s1 - s2) mod n
    # d = (s*k - z) / r mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = mod_inverse(s_diff, n)
    if s_diff_inv is None:
        return None
    
    k = (z_diff * s_diff_inv) % n
    
    # Now recover d from first signature
    r_inv = mod_inverse(r, n)
    if r_inv is None:
        return None
    
    d = (r_inv * ((s1 * k - z1) % n)) % n
    
    return d, k

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # Find signatures with same r value (nonce reuse)
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find r values that appear multiple times
    for r, indices in r_map.items():
        if len(indices) >= 2:
            # We have nonce reuse!
            idx1, idx2 = indices[0], indices[1]
            
            sig1 = signatures[idx1]
            sig2 = signatures[idx2]
            
            r_val = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            result = solve_ecdsa_nonce_reuse(r_val, s1, s2, z1, z2, n)
            
            if result:
                d, k = result
                
                # Format as 64 character lowercase hex
                d_hex = format(d, '064x')
                k_hex = format(k, '064x')
                
                output = {
                    "d": d_hex,
                    "k": k_hex
                }
                
                print(json.dumps(output))
                return

if __name__ == "__main__":
    main()
