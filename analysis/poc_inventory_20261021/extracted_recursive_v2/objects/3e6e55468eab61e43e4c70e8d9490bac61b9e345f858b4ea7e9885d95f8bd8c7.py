import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
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

def recover_private_key(sigs, n):
    """Recover private key from signatures with repeated nonce."""
    # Find signatures with same r value (repeated nonce)
    r_map = {}
    for i, sig in enumerate(sigs):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find a pair with same r
    for r_val, indices in r_map.items():
        if len(indices) >= 2:
            # Use first two signatures with same r
            i1, i2 = indices[0], indices[1]
            
            r = int(sigs[i1]['r'], 16)
            s1 = int(sigs[i1]['s'], 16)
            z1 = int(sigs[i1]['z'], 16)
            s2 = int(sigs[i2]['s'], 16)
            z2 = int(sigs[i2]['z'], 16)
            
            # From s1 - s2 = k^-1 * (z1 - z2) mod n
            # So k = (z1 - z2) / (s1 - s2) mod n
            ds = (s1 - s2) % n
            dz = (z1 - z2) % n
            
            if ds == 0:
                continue
                
            k = (dz * modinv(ds, n)) % n
            
            # From s1 = k^-1 * (z1 + r*d) mod n
            # So d = (s1*k - z1) / r mod n
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            return d, k
    
    return None, None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    sigs = instance['signatures']
    
    # Recover private key
    d, k = recover_private_key(sigs, n)
    
    if d is None:
        # Fallback: shouldn't happen with this instance
        d = 0
        k = 0
    
    # Format output
    result = {
        "d": f"{d:064x}",
        "k": f"{k:064x}"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
