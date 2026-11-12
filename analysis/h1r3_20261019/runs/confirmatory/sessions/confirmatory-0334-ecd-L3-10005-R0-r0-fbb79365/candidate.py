import sys
import json
from collections import defaultdict

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Group signatures by r value
    r_groups = defaultdict(list)
    for idx, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        r_groups[r].append((idx, r, s, z))
    
    # Look for repeated r values (nonce reuse)
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Found nonce reuse! Use first two signatures
            idx1, r1, s1, z1 = sigs[0]
            idx2, r2, s2, z2 = sigs[1]
            
            # Calculate k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            denom_inv = modinv(denominator, n)
            if denom_inv is None:
                continue
                
            k = (numerator * denom_inv) % n
            
            # Calculate private key: d = (s1 * k - z1) / r mod n
            numerator = (s1 * k - z1) % n
            r_inv = modinv(r, n)
            
            if r_inv is None:
                continue
                
            private_key = (numerator * r_inv) % n
            
            result = {
                "status": "UNDERDETERMINED",
                "reason": f"nonce reuse detected for r={hex(r)[:16]}..., recovered private key"
            }
            print(json.dumps(result))
            return
    
    # No nonce reuse found
    result = {
        "status": "UNDERDETERMINED",
        "reason": "no exploitable nonce reuse detected in signatures"
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
