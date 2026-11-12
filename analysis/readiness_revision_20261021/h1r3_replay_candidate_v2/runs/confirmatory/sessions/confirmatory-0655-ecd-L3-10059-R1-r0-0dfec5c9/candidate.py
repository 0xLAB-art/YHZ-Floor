import sys
import json

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

def recover_private_key(signatures):
    """Recover private key from ECDSA signatures with nonce reuse."""
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with same r value (nonce reuse)
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find a pair with nonce reuse
    for r, indices in r_map.items():
        if len(indices) >= 2:
            # Use first two signatures with same r
            i, j = indices[0], indices[1]
            
            r_val = r
            s1 = int(signatures[i]['s'], 16)
            s2 = int(signatures[j]['s'], 16)
            z1 = int(signatures[i]['z'], 16)
            z2 = int(signatures[j]['z'], 16)
            
            # Recover nonce k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k = (numerator * modinv(denominator, n)) % n
            
            # Recover private key d: d = (s*k - z) / r mod n
            d = ((s1 * k - z1) * modinv(r_val, n)) % n
            
            # Format as 64 hex characters
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            return d_hex, k_hex
    
    raise ValueError("No nonce reuse found")

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # Recover private key and nonce
    d_hex, k_hex = recover_private_key(signatures)
    
    # Output result
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
