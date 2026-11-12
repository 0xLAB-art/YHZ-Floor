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
    Recover private key from ECDSA signatures with repeated nonce (r value).
    
    For ECDSA: s = k^(-1) * (z + r*d) mod n
    If two signatures share the same k (same r):
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    Then: s1 - s2 = k^(-1) * (z1 - z2) mod n
    So: k = (z1 - z2) * (s1 - s2)^(-1) mod n
    And: d = (s*k - z) * r^(-1) mod n
    """
    
    # Find signatures with the same r value
    r_dict = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        if r not in r_dict:
            r_dict[r] = []
        r_dict[r].append(sig)
    
    # Find a pair with repeated r
    for r_val, sigs in r_dict.items():
        if len(sigs) >= 2:
            sig1 = sigs[0]
            sig2 = sigs[1]
            
            r = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Calculate k
            z_diff = (z1 - z2) % n
            s_diff = (s1 - s2) % n
            
            if s_diff == 0:
                continue
                
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Calculate private key d
            r_inv = modinv(r, n)
            d = ((s1 * k - z1) * r_inv) % n
            
            return d
    
    return None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Recover private key
    d = recover_private_key(signatures, n)
    
    if d is None:
        # Fallback: shouldn't happen with the given data
        d = 0
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
