import sys
import json

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find duplicate r values
    r_map = {}
    for idx, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(idx)
    
    # Find nonce reuse
    for r, indices in r_map.items():
        if len(indices) >= 2:
            # Use first two signatures with same r
            i, j = indices[0], indices[1]
            
            r_val = int(signatures[i]['r'], 16)
            s1 = int(signatures[i]['s'], 16)
            z1 = int(signatures[i]['z'], 16)
            s2 = int(signatures[j]['s'], 16)
            z2 = int(signatures[j]['z'], 16)
            
            # Recover nonce k
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Recover private key d
            d = (((s1 * k - z1) % n) * modinv(r_val, n)) % n
            
            # Format as 64 hex characters
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            
            print(json.dumps(result))
            return
    
    # Should not reach here if vulnerability exists
    raise ValueError("No nonce reuse found")

if __name__ == "__main__":
    main()