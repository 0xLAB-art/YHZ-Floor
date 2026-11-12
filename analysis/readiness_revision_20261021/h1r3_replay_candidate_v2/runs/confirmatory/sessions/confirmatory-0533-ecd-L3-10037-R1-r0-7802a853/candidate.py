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
    """Extended Euclidean algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(signatures, n):
    """
    Recover private key from ECDSA signatures with repeated nonce.
    For signatures with same r value, we have:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    Therefore:
    s1 - s2 = k^(-1) * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    
    # Group signatures by r value
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append({'s': s, 'z': z, 'r': r})
    
    # Find r values that appear more than once
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1 = sigs[0]
            sig2 = sigs[1]
            
            s1, z1 = sig1['s'], sig1['z']
            s2, z2 = sig2['s'], sig2['z']
            
            # Calculate k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
                
            k = (numerator * modinv(denominator, n)) % n
            
            if k == 0:
                continue
            
            # Calculate d = (s*k - z) / r mod n
            numerator = (s1 * k - z1) % n
            denominator = r % n
            
            if denominator == 0:
                continue
                
            d = (numerator * modinv(denominator, n)) % n
            
            return d, k
    
    return None, None

def main():
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # Recover private key
    d, k = recover_private_key(signatures, n)
    
    if d is None:
        # Fallback: should not happen with this instance
        d = 0
        k = 0
    
    # Format output
    result = {
        "d": format(d, '064x'),
        "k": format(k, '064x')
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
