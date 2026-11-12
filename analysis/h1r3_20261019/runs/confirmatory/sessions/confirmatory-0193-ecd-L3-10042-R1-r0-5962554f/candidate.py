import sys
import json

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm"""
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

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Convert hex to integers
    sigs = []
    for sig in signatures:
        sigs.append({
            'r': int(sig['r'], 16),
            's': int(sig['s'], 16),
            'z': int(sig['z'], 16)
        })
    
    # Find duplicate r values (nonce reuse)
    r_to_indices = {}
    for i, sig in enumerate(sigs):
        r = sig['r']
        if r not in r_to_indices:
            r_to_indices[r] = []
        r_to_indices[r].append(i)
    
    # Find a pair with the same r
    k = None
    d = None
    
    for r, indices in r_to_indices.items():
        if len(indices) >= 2:
            # Found nonce reuse!
            i1, i2 = indices[0], indices[1]
            sig1, sig2 = sigs[i1], sigs[i2]
            
            r = sig1['r']
            s1 = sig1['s']
            s2 = sig2['s']
            z1 = sig1['z']
            z2 = sig2['z']
            
            # Recover k: k = (z1 - z2) / (s1 - s2) mod n
            z_diff = (z1 - z2) % n
            s_diff = (s1 - s2) % n
            
            if s_diff == 0:
                continue
                
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Recover d: d = (s*k - z) / r mod n
            r_inv = modinv(r, n)
            d = ((s1 * k - z1) * r_inv) % n
            
            break
    
    # Format as 64 hex characters (lowercase, zero-padded)
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
