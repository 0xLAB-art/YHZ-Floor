import sys
import json
import hashlib

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
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
    
    # SECP256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    signatures = []
    for sig in data['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append({'r': r, 's': s, 'z': z})
    
    # Find duplicate r values (nonce reuse)
    r_map = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find a pair with the same r
    for r, indices in r_map.items():
        if len(indices) >= 2:
            # We found nonce reuse!
            i1, i2 = indices[0], indices[1]
            sig1 = signatures[i1]
            sig2 = signatures[i2]
            
            r = sig1['r']
            s1 = sig1['s']
            s2 = sig2['s']
            z1 = sig1['z']
            z2 = sig2['z']
            
            # Recovery formulas:
            # s1 = (z1 + r*d) / k mod n
            # s2 = (z2 + r*d) / k mod n
            # s1 - s2 = (z1 - z2) / k mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            # k = z_diff * modinv(s_diff, n) mod n
            k = (z_diff * modinv(s_diff, n)) % n
            
            # d = (s*k - z) / r mod n
            d = ((s1 * k - z1) % n * modinv(r, n)) % n
            
            # Format as 64 lowercase hex characters
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            
            print(json.dumps(result))
            return
    
    # If no nonce reuse found, something is wrong
    raise Exception("No nonce reuse detected")

if __name__ == "__main__":
    main()