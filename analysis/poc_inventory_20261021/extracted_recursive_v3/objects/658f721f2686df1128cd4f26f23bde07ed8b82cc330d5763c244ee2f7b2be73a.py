import json
import sys

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def recover_key_from_reused_nonce(sig1, sig2, n):
    """Recover private key when two signatures share the same r (nonce reuse)"""
    r1 = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    
    r2 = int(sig2['r'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Verify r values match
    if r1 != r2:
        return None, None
    
    r = r1
    
    # Recover k: k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None, None
    
    k = (numerator * modinv(denominator, n)) % n
    
    # Recover d: d = (s*k - z) / r mod n
    numerator_d = (s1 * k - z1) % n
    d = (numerator_d * modinv(r, n)) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with same r value
    r_to_sigs = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append(i)
    
    # Find reused nonces
    d = None
    k = None
    
    for r_val, indices in r_to_sigs.items():
        if len(indices) >= 2:
            # Found nonce reuse
            sig1 = signatures[indices[0]]
            sig2 = signatures[indices[1]]
            d, k = recover_key_from_reused_nonce(sig1, sig2, n)
            if d is not None:
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