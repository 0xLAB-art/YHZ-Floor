import sys
import json
from math import gcd

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    if gcd(a, m) != 1:
        return None
    u1, u2, u3 = 1, 0, a
    v1, v2, v3 = 0, 1, m
    while v3 != 0:
        q = u3 // v3
        v1, v2, v3, u1, u2, u3 = (u1 - q * v1), (u2 - q * v2), (u3 - q * v3), v1, v2, v3
    return u1 % m

def recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n):
    """
    Recover private key k from two signatures with the same nonce.
    If r values are equal, nonces are the same.
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    # Calculate k (the nonce)
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None
    
    denom_inv = modinv(denominator, n)
    if denom_inv is None:
        return None
    
    k = (numerator * denom_inv) % n
    
    # Calculate d (private key) using first signature
    r_inv = modinv(r, n)
    if r_inv is None:
        return None
    
    d = (((s1 * k - z1) % n) * r_inv) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Look for repeated r values (nonce reuse)
    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            r1 = int(signatures[i]['r'], 16)
            r2 = int(signatures[j]['r'], 16)
            
            if r1 == r2:
                # Found nonce reuse!
                s1 = int(signatures[i]['s'], 16)
                s2 = int(signatures[j]['s'], 16)
                z1 = int(signatures[i]['z'], 16)
                z2 = int(signatures[j]['z'], 16)
                
                d = recover_private_key_from_nonce_reuse(r1, s1, s2, z1, z2, n)
                
                if d is not None:
                    # Format as 64 lowercase hex characters
                    d_hex = format(d, '064x')
                    print(json.dumps({"d": d_hex}))
                    return
    
    # Should not reach here if instance is valid
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()