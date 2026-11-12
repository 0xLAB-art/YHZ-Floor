import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_key_from_nonce_reuse(r, s1, z1, s2, z2, n):
    """Recover private key d and nonce k from two signatures with same r"""
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # d = (s*k - z) / r mod n
    d = ((s1 * k - z1) % n * modinv(r, n)) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Convert signatures to integers
    sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sigs.append((r, s, z))
    
    # Find signatures with same r value (nonce reuse)
    r_map = {}
    for i, (r, s, z) in enumerate(sigs):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find a pair with reused nonce
    d = None
    k = None
    
    for r, sig_list in r_map.items():
        if len(sig_list) >= 2:
            # Found nonce reuse
            _, s1, z1 = sig_list[0]
            _, s2, z2 = sig_list[1]
            
            try:
                d, k = recover_key_from_nonce_reuse(r, s1, z1, s2, z2, n)
                break
            except:
                continue
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()