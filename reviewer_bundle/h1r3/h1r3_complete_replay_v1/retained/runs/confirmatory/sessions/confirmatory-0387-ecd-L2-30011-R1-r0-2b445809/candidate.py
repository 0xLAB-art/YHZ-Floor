import sys
import json

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
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def recover_private_key(sigs):
    """Recover private key from ECDSA signatures with repeated nonce."""
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with the same r value
    r_groups = {}
    for i, sig in enumerate(sigs):
        r = int(sig['r'], 16)
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(i)
    
    # Find a pair with repeated r
    for r_val, indices in r_groups.items():
        if len(indices) >= 2:
            # Use first two signatures with same r
            idx1, idx2 = indices[0], indices[1]
            
            r = int(sigs[idx1]['r'], 16)
            s1 = int(sigs[idx1]['s'], 16)
            z1 = int(sigs[idx1]['z'], 16)
            s2 = int(sigs[idx2]['s'], 16)
            z2 = int(sigs[idx2]['z'], 16)
            
            # Recover k: k = (z1 - z2) / (s1 - s2) mod n
            k = ((z1 - z2) * modinv((s1 - s2) % n, n)) % n
            
            # Recover d: d = (s*k - z) / r mod n
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            return d
    
    raise ValueError("No repeated nonce found")

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # Recover private key
    d = recover_private_key(signatures)
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
