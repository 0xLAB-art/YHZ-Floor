import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def recover_private_key(signatures):
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with the same r value (same nonce k)
    r_dict = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_dict:
            r_dict[r] = []
        r_dict[r].append((i, sig))
    
    # Look for duplicate r values
    for r, sigs in r_dict.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1 = sigs[0][1]
            sig2 = sigs[1][1]
            
            r = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Calculate k from the two signatures
            # k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k = (numerator * modinv(denominator, n)) % n
            
            # Calculate private key d from k
            # d = (s * k - z) / r mod n
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            return d
    
    return None

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    d = recover_private_key(signatures)
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()