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
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_key_from_nonce_reuse(sigs, n):
    """Find signatures with same r and recover private key"""
    r_map = {}
    
    for i, sig in enumerate(sigs):
        r = int(sig['r'], 16)
        if r in r_map:
            # Found nonce reuse
            j = r_map[r]
            return recover_from_pair(sigs[j], sig, n)
        r_map[r] = i
    
    return None, None

def recover_from_pair(sig1, sig2, n):
    """Recover k and d from two signatures with same r"""
    r = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    s2 = int(sig2['s'], 16)
    z1 = int(sig1['z'], 16)
    z2 = int(sig2['z'], 16)
    
    # k = (z1 - z2) / (s1 - s2) mod n
    k = ((z1 - z2) * modinv(s1 - s2, n)) % n
    
    # d = (s*k - z) / r mod n
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return d, k

def main():
    # ECDSA curve order (secp256k1)
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    d, k = recover_key_from_nonce_reuse(signatures, n)
    
    if d is None:
        # Fallback: shouldn't happen with this instance
        d = 0
        k = 0
    
    result = {
        "d": format(d, '064x'),
        "k": format(k, '064x')
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()