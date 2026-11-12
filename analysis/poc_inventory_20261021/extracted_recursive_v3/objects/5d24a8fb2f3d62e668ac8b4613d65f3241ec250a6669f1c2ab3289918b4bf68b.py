import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
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

def recover_private_key(signatures, n):
    """
    Recover private key from ECDSA signatures with reused nonce.
    
    If two signatures share the same r value, they used the same k (nonce).
    Given: s1 = k^-1(z1 + r*d) mod n
           s2 = k^-1(z2 + r*d) mod n
    
    We can solve for k and then d.
    """
    # Find signatures with matching r values
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find a pair with matching r
    for r, indices in r_map.items():
        if len(indices) >= 2:
            i1, i2 = indices[0], indices[1]
            sig1 = signatures[i1]
            sig2 = signatures[i2]
            
            r_val = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Recover k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k = (numerator * modinv(denominator, n)) % n
            
            if k == 0:
                continue
            
            # Recover d: d = (s*k - z) / r mod n
            d = ((s1 * k - z1) % n * modinv(r_val, n)) % n
            
            return d, k
    
    return None, None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Recover private key
    d, k = recover_private_key(signatures, n)
    
    if d is None:
        # Fallback: shouldn't happen with the given data
        d = 0
        k = 0
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        'd': d_hex,
        'k': k_hex
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()