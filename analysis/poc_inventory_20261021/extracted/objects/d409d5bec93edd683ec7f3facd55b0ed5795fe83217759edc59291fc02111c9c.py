import sys
import json
from collections import defaultdict

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
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
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    pub_x = int(data['public_key']['x'], 16)
    pub_y = int(data['public_key']['y'], 16)
    
    # Parse signatures
    signatures = []
    for sig in data['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # Look for repeated r values (nonce reuse attack)
    r_groups = defaultdict(list)
    for i, (r, s, z) in enumerate(signatures):
        r_groups[r].append((s, z, i))
    
    # Find pairs with same r
    for r, group in r_groups.items():
        if len(group) >= 2:
            # Use first two signatures with same r
            s1, z1, _ = group[0]
            s2, z2, _ = group[1]
            
            # Recover k (nonce) and d (private key)
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s*k - z) / r mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            s_diff_inv = modinv(s_diff, n)
            if s_diff_inv is None:
                continue
            
            k = (z_diff * s_diff_inv) % n
            
            # Recover private key d using first signature
            r_inv = modinv(r, n)
            if r_inv is None:
                continue
            
            d = (r_inv * (s1 * k - z1)) % n
            
            # Format output
            result = {
                "d": format(d, '064x'),
                "k": format(k, '064x')
            }
            
            print(json.dumps(result))
            return
    
    # If no repeated r found, return error (shouldn't happen for this instance)
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()
