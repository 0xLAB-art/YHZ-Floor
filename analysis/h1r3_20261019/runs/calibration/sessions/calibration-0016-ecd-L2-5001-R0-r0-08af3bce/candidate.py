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
    
    # Extract public key
    x = int(instance['public_key']['x'], 16)
    y = int(instance['public_key']['y'], 16)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Extract signatures
    sigs = instance['signatures']
    
    # Look for duplicate r values (nonce reuse)
    r_map = {}
    for i, sig in enumerate(sigs):
        r = int(sig['r'], 16)
        if r in r_map:
            # Found duplicate r - nonce reuse attack
            j = r_map[r]
            
            r1 = int(sigs[j]['r'], 16)
            s1 = int(sigs[j]['s'], 16)
            z1 = int(sigs[j]['z'], 16)
            
            r2 = int(sigs[i]['r'], 16)
            s2 = int(sigs[i]['s'], 16)
            z2 = int(sigs[i]['z'], 16)
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s1 * k - z1) / r1 mod n
            
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k = (numerator * modinv(denominator, n)) % n
            
            # Calculate private key
            numerator_d = (s1 * k - z1) % n
            denominator_d = r1 % n
            d = (numerator_d * modinv(denominator_d, n)) % n
            
            # Format as 64 hex characters
            d_hex = format(d, '064x')
            
            result = {"d": d_hex}
            print(json.dumps(result))
            return
        else:
            r_map[r] = i
    
    # Should not reach here if nonce reuse exists
    result = {"d": "0" * 64}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
