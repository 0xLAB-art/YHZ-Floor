import sys
import json
import hashlib

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_key_from_reused_nonce(sig1, sig2, n):
    """Recover private key from two signatures with same r (reused nonce)"""
    r1 = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    
    r2 = int(sig2['r'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    if r1 != r2:
        return None, None
    
    r = r1
    
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None, None
    
    k = (numerator * modinv(denominator, n)) % n
    
    # d = (s*k - z) / r mod n
    numerator_d = (s1 * k - z1) % n
    d = (numerator_d * modinv(r, n)) % n
    
    return d, k

def main():
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # Find signatures with same r
    r_map = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find reused nonces
    d = None
    k = None
    
    for r, indices in r_map.items():
        if len(indices) >= 2:
            # Found reused nonce
            sig1 = signatures[indices[0]]
            sig2 = signatures[indices[1]]
            d, k = recover_key_from_reused_nonce(sig1, sig2, n)
            if d is not None:
                break
    
    if d is None:
        # No reused nonces found, output zeros
        d = 0
        k = 0
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()