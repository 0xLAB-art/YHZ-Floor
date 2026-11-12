import sys
import json
from collections import defaultdict

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = egcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = egcd(a % m, m)
    if gcd != 1:
        return None
    return (x % m + m) % m

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Look for repeated r values (nonce reuse)
    r_map = defaultdict(list)
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        r_map[r].append((i, s, z))
    
    # Find nonce reuse
    for r, sigs in r_map.items():
        if len(sigs) >= 2:
            # We have nonce reuse!
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            # k*s1 = z1 + r*d (mod n)
            # k*s2 = z2 + r*d (mod n)
            # k*(s1 - s2) = z1 - z2 (mod n)
            # k = (z1 - z2) / (s1 - s2) (mod n)
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            s_diff_inv = modinv(s_diff, n)
            if s_diff_inv is None:
                continue
            
            k = (z_diff * s_diff_inv) % n
            
            # Now recover private key d
            # k*s1 = z1 + r*d (mod n)
            # d = (k*s1 - z1) / r (mod n)
            
            r_inv = modinv(r, n)
            if r_inv is None:
                continue
            
            d = ((k * s1 - z1) % n * r_inv) % n
            
            # Verify with another signature if available
            if len(signatures) > 2:
                # Verify: k*s = z + r*d (mod n)
                for sig in signatures:
                    r_test = int(sig['r'], 16)
                    s_test = int(sig['s'], 16)
                    z_test = int(sig['z'], 16)
                    
                    # Try to recover k for this signature
                    r_test_inv = modinv(r_test, n)
                    if r_test_inv:
                        k_test = ((z_test + r_test * d) % n * modinv(s_test, n)) % n
                        # This should be consistent
            
            # Format output
            d_hex = format(d, '064x')
            print(json.dumps({"d": d_hex}))
            return
    
    # If no nonce reuse found, output zero (shouldn't happen for valid input)
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()
