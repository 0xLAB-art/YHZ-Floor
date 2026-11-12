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
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    Qx = int(instance['public_key']['x'], 16)
    Qy = int(instance['public_key']['y'], 16)
    
    # Parse signatures
    sigs = instance['signatures']
    
    # Look for repeated r values (nonce reuse attack)
    r_dict = {}
    for i, sig in enumerate(sigs):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r in r_dict:
            # Found nonce reuse! Extract private key
            j, s1, z1 = r_dict[r]
            s2 = s
            z2 = z
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s1*k - z1) / r mod n
            
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k = (numerator * modinv(denominator, n)) % n
            
            # Calculate d from first signature
            d = (((s1 * k - z1) % n) * modinv(r, n)) % n
            
            # Output result
            result = {"d": format(d, '064x')}
            print(json.dumps(result))
            return
        
        r_dict[r] = (i, s, z)
    
    # If no nonce reuse found, output error (shouldn't happen with valid input)
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()