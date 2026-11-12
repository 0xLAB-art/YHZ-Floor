import sys
import json


def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm"""
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
    
    # SECP256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Find duplicate r values
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find a pair with the same r
    d = None
    k = None
    
    for r_val, indices in r_map.items():
        if len(indices) >= 2:
            # We have nonce reuse!
            i1, i2 = indices[0], indices[1]
            
            r = r_val
            s1 = int(signatures[i1]['s'], 16)
            z1 = int(signatures[i1]['z'], 16)
            s2 = int(signatures[i2]['s'], 16)
            z2 = int(signatures[i2]['z'], 16)
            
            # From ECDSA: s = k^(-1) * (z + r*d) mod n
            # s1 = k^(-1) * (z1 + r*d) mod n
            # s2 = k^(-1) * (z2 + r*d) mod n
            # 
            # s1 - s2 = k^(-1) * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
                
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Now recover d from: s1 = k^(-1) * (z1 + r*d) mod n
            # s1 * k = z1 + r*d mod n
            # d = (s1*k - z1) / r mod n
            
            k_inv = modinv(k, n)
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            # Verify with the second signature
            verify = (z2 + r * d) * k_inv % n
            if verify == s2:
                break
            else:
                # Try negative k
                k = (-k) % n
                k_inv = modinv(k, n)
                d = ((s1 * k - z1) * modinv(r, n)) % n
                verify = (z2 + r * d) * k_inv % n
                if verify == s2:
                    break
    
    # Format output
    result = {
        "d": format(d, '064x'),
        "k": format(k, '064x')
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
