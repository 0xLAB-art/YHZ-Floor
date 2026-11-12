import json
import sys

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
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
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    Qx = int(data['public_key']['x'], 16)
    Qy = int(data['public_key']['y'], 16)
    
    # Parse signatures
    signatures = []
    for sig in data['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # Look for repeated r values (nonce reuse)
    r_dict = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_dict:
            r_dict[r].append((i, s, z))
        else:
            r_dict[r] = [(i, s, z)]
    
    # Find pairs with same r
    private_key = None
    for r, occurrences in r_dict.items():
        if len(occurrences) >= 2:
            # Use first two occurrences
            idx1, s1, z1 = occurrences[0]
            idx2, s2, z2 = occurrences[1]
            
            # Calculate k from nonce reuse
            # k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k = (numerator * modinv(denominator, n)) % n
            
            # Calculate private key d from k
            # d = (s*k - z) / r mod n
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            # Verify with second signature
            d_check = ((s2 * k - z2) * modinv(r, n)) % n
            
            if d == d_check and d != 0:
                private_key = d
                nonce = k
                break
    
    # Format output
    d_hex = format(private_key, '064x')
    k_hex = format(nonce, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
