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
        instance = json.load(f)
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find duplicate r values
    r_to_sigs = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((i, sig))
    
    # Find a pair with same r
    d = None
    k = None
    
    for r_val, sigs in r_to_sigs.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1 = sigs[0][1]
            sig2 = sigs[1][1]
            
            r = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Compute private key: d = (s1*z2 - s2*z1) / (s1*r - s2*r) mod n
            # Simplify: d = (s1*z2 - s2*z1) / (r*(s1 - s2)) mod n
            numerator = (s1 * z2 - s2 * z1) % n
            denominator = (r * (s1 - s2)) % n
            
            try:
                d = (numerator * modinv(denominator, n)) % n
                
                # Compute nonce: k = (z1 + r*d) / s1 mod n
                k = ((z1 + r * d) % n * modinv(s1, n)) % n
                
                # Verify with the signature
                # Check: r == (k * G).x mod n (we'll verify s instead)
                s_check = (modinv(k, n) * (z1 + r * d)) % n
                if s_check == s1:
                    break
            except:
                continue
    
    # Format output
    result = {
        "d": format(d, '064x'),
        "k": format(k, '064x')
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
