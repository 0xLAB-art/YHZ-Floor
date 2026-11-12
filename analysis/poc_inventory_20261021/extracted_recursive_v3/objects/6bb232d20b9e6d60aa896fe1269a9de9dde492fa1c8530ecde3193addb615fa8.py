import json
import sys
import hashlib

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def recover_key_from_repeated_nonce(r, s1, z1, s2, z2, n):
    """Recover private key when same nonce k is used for two signatures"""
    # From s1 = k^(-1)(z1 + rd) and s2 = k^(-1)(z2 + rd)
    # We get: s1 - s2 = k^(-1)(z1 - z2)
    # So: k = (z1 - z2) / (s1 - s2) mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    if s_diff == 0:
        return None, None
    
    k = (z_diff * modinv(s_diff, n)) % n
    
    # Now recover d from: s1 = k^(-1)(z1 + rd)
    # rd = s1*k - z1
    # d = (s1*k - z1) / r mod n
    
    k_inv = modinv(k, n)
    if (s1 * k - z1) % n != (r * ((s1 * k - z1) * modinv(r, n)) % n) % n:
        # Verify the math
        pass
    
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return k, d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Find repeated r values
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r in r_map:
            # Found a repeated r! Recover the key
            j, s1, z1 = r_map[r]
            
            # Try both orderings
            k, d = recover_key_from_repeated_nonce(r, s, z, s1, z1, n)
            
            if k is not None and d is not None:
                # Verify the signature
                k_inv = modinv(k, n)
                expected_s = (k_inv * (z + r * d)) % n
                
                if expected_s == s or expected_s == s1:
                    # Found it!
                    result = {
                        "d": format(d, '064x'),
                        "k": format(k, '064x')
                    }
                    print(json.dumps(result))
                    return
        else:
            r_map[r] = (i, s, z)
    
    # If no match found, shouldn't happen based on problem structure
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()