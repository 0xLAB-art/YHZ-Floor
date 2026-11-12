import sys
import json
import base64

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

def mod_inverse(a, m):
    # Extended Euclidean Algorithm
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
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
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    signatures = []
    for sig in data['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # Find duplicate r values (nonce reuse)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find nonce reuse
    d = None
    k = None
    
    for r, sigs in r_map.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            try:
                s_diff_inv = mod_inverse(s_diff, n)
                k_recovered = (z_diff * s_diff_inv) % n
                
                # d = (s*k - z) / r mod n
                k_inv = mod_inverse(k_recovered, n)
                d_recovered = (r * k_inv * (s1 * k_recovered - z1)) % n
                
                # Verify with second signature
                d_verify = (r * k_inv * (s2 * k_recovered - z2)) % n
                
                if d_recovered == d_verify:
                    d = d_recovered
                    k = k_recovered
                    break
            except:
                continue
    
    # If no nonce reuse found, try alternative: s*k = z + r*d
    if d is None:
        for r, sigs in r_map.items():
            if len(sigs) >= 2:
                i1, s1, z1 = sigs[0]
                i2, s2, z2 = sigs[1]
                
                # From s1*k = z1 + r*d and s2*k = z2 + r*d
                # s1*k - s2*k = z1 - z2
                # k(s1 - s2) = z1 - z2
                s_diff = (s1 - s2) % n
                z_diff = (z1 - z2) % n
                
                if s_diff != 0:
                    try:
                        s_diff_inv = mod_inverse(s_diff, n)
                        k_recovered = (z_diff * s_diff_inv) % n
                        
                        # Now solve for d: s1*k = z1 + r*d
                        # r*d = s1*k - z1
                        # d = (s1*k - z1) / r
                        r_inv = mod_inverse(r, n)
                        d_recovered = ((s1 * k_recovered - z1) * r_inv) % n
                        
                        d = d_recovered
                        k = k_recovered
                        break
                    except:
                        continue
    
    result = {
        "d": int_to_hex(d),
        "k": int_to_hex(k)
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()