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
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def recover_private_key(sigs):
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with the same r value
    r_map = {}
    for i, sig in enumerate(sigs):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Look for duplicate r values
    for r, indices in r_map.items():
        if len(indices) >= 2:
            # Use first two signatures with same r
            i1, i2 = indices[0], indices[1]
            sig1, sig2 = sigs[i1], sigs[i2]
            
            r = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Calculate k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k = (numerator * modinv(denominator, n)) % n
            
            # Calculate d = (s*k - z) / r mod n
            numerator = (s1 * k - z1) % n
            d = (numerator * modinv(r, n)) % n
            
            # Format as 64 character hex strings
            k_hex = format(k, '064x')
            d_hex = format(d, '064x')
            
            return k_hex, d_hex
    
    return None, None

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # Recover the private key
    k_hex, d_hex = recover_private_key(signatures)
    
    # Output result
    result = {
        "d": d_hex,
        "k": k_hex
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
