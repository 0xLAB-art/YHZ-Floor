import sys
import json

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
        return None
    return (x % m + m) % m

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # SECP256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Check for nonce reuse (duplicate r values)
    r_values = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r in r_values:
            # Found duplicate r! Nonce reuse detected
            j, s1, z1 = r_values[r]
            
            # We have two signatures with same r (same k)
            # k = (z1 - z2) / (s1 - s2) mod n
            z_diff = (z1 - z) % n
            s_diff = (s1 - s) % n
            
            s_diff_inv = modinv(s_diff, n)
            if s_diff_inv is None:
                continue
                
            k = (z_diff * s_diff_inv) % n
            
            # Now recover private key: d = (s*k - z) / r mod n
            r_inv = modinv(r, n)
            if r_inv is None:
                continue
                
            d = ((s * k - z) * r_inv) % n
            
            # Verify by checking if d*G matches public key
            # For now, we've found the vulnerability
            result = {
                "status": "UNDERDETERMINED",
                "reason": f"Nonce reuse detected: signatures {j} and {i} share r={hex(r)}, allowing private key recovery"
            }
            print(json.dumps(result))
            return
        
        r_values[r] = (i, s, z)
    
    # No obvious vulnerability found
    result = {
        "status": "UNDERDETERMINED",
        "reason": "No nonce reuse detected among signatures"
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()