import sys
import json


def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        return None
    return (x % m + m) % m

def recover_key_from_duplicate_nonce(r, s1, z1, s2, z2, n):
    """Recover private key from two signatures with same nonce"""
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None, None
    
    denom_inv = modinv(denominator, n)
    if denom_inv is None:
        return None, None
    
    k = (numerator * denom_inv) % n
    
    # d = (s * k - z) / r mod n
    r_inv = modinv(r, n)
    if r_inv is None:
        return None, None
    
    d = (((s1 * k - z1) % n) * r_inv) % n
    
    return k, d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sigs.append((r, s, z))
    
    # Find duplicate r values
    r_map = {}
    for i, (r, s, z) in enumerate(sigs):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find duplicates and recover key
    d = None
    k = None
    
    for r, occurrences in r_map.items():
        if len(occurrences) >= 2:
            # Use first two occurrences
            i1, s1, z1 = occurrences[0]
            i2, s2, z2 = occurrences[1]
            
            k_recovered, d_recovered = recover_key_from_duplicate_nonce(r, s1, z1, s2, z2, n)
            
            if d_recovered is not None:
                d = d_recovered
                k = k_recovered
                break
    
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
