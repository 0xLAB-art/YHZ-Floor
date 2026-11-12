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

def recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n):
    """
    Recover private key k (nonce) and d (private key) from two signatures
    that reused the same nonce.
    
    From ECDSA:
    s1 = k^(-1) * (z1 + r * d) mod n
    s2 = k^(-1) * (z2 + r * d) mod n
    
    Therefore:
    s1 - s2 = k^(-1) * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    
    Then:
    d = (s * k - z) / r mod n
    """
    # Calculate k (the nonce)
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # Calculate d (the private key)
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return k, d

def find_nonce_reuse(signatures, n):
    """Find two signatures with the same r value (nonce reuse)."""
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r in r_map:
            return r_map[r], i
        r_map[r] = i
    return None, None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find nonce reuse
    idx1, idx2 = find_nonce_reuse(signatures, n)
    
    if idx1 is None:
        # No nonce reuse found, output empty result
        result = {"d": "0" * 64, "k": "0" * 64}
    else:
        sig1 = signatures[idx1]
        sig2 = signatures[idx2]
        
        r = int(sig1['r'], 16)
        s1 = int(sig1['s'], 16)
        s2 = int(sig2['s'], 16)
        z1 = int(sig1['z'], 16)
        z2 = int(sig2['z'], 16)
        
        # Recover the private key and nonce
        k, d = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
        
        # Format as 64 character hex strings
        result = {
            "d": format(d, '064x'),
            "k": format(k, '064x')
        }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()