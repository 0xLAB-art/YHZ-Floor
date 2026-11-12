import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
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

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    Qx = int(instance['public_key']['x'], 16)
    Qy = int(instance['public_key']['y'], 16)
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # Look for repeated r values (nonce reuse)
    r_dict = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_dict:
            r_dict[r] = []
        r_dict[r].append((i, s, z))
    
    # Find pairs with same r
    for r, pairs in r_dict.items():
        if len(pairs) >= 2:
            # We have nonce reuse!
            i1, s1, z1 = pairs[0]
            i2, s2, z2 = pairs[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s1 * k - z1) / r mod n
            
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k = (numerator * modinv(denominator, n)) % n
            
            # Recover private key d
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            # Verify by checking if d * G = Q
            # For this problem, we'll format and return the answer
            
            result = {
                "d": format(d, '064x'),
                "k": format(k, '064x')
            }
            
            print(json.dumps(result))
            return
    
    # If no nonce reuse found, should not happen based on problem
    result = {
        "d": "0" * 64,
        "k": "0" * 64
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()