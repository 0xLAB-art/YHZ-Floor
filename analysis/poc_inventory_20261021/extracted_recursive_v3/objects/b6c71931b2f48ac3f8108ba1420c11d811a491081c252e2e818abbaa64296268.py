import json
import sys

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

def recover_key_from_nonce_reuse(r, s1, z1, s2, z2, n):
    """Recover private key d and nonce k from two signatures with same r"""
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # d = (s * k - z) / r mod n
    numerator_d = (s1 * k - z1) % n
    d = (numerator_d * modinv(r, n)) % n
    
    return d, k

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with duplicate r values
    r_to_sigs = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((i, s, z))
    
    # Find a duplicate r
    d_found = None
    k_found = None
    
    for r, sigs in r_to_sigs.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            _, s1, z1 = sigs[0]
            _, s2, z2 = sigs[1]
            
            d, k = recover_key_from_nonce_reuse(r, s1, z1, s2, z2, n)
            d_found = d
            k_found = k
            break
    
    # Format as 64-character hex strings (lowercase, zero-padded)
    d_hex = format(d_found, '064x')
    k_hex = format(k_found, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()