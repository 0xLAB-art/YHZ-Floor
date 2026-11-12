import json
import sys

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
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Extract public key
    Qx = int(instance['public_key']['x'], 16)
    Qy = int(instance['public_key']['y'], 16)
    
    # Extract signatures
    signatures = instance['signatures']
    
    # Look for repeated r values (nonce reuse attack)
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r in r_map:
            # Found duplicate r! We can recover the private key
            j, s1, z1 = r_map[r]
            s2, z2 = s, z
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s*k - z) / r mod n
            
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k = (numerator * modinv(denominator, n)) % n
            
            # Calculate private key d
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            # Verify with the other signature too
            d_check = ((s2 * k - z2) * modinv(r, n)) % n
            
            if d == d_check:
                # Format output
                d_hex = format(d, '064x')
                k_hex = format(k, '064x')
                
                result = {
                    "d": d_hex,
                    "k": k_hex
                }
                
                print(json.dumps(result))
                return
        else:
            r_map[r] = (i, s, z)
    
    # Should not reach here if instance is valid
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()
