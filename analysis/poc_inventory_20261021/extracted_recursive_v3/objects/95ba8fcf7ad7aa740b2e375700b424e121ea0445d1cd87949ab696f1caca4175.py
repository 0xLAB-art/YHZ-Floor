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

def recover_key_from_nonce_reuse(sig1, sig2, n):
    """Recover private key when two signatures share the same nonce (same r value)"""
    r = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Calculate k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # Calculate d = (s*k - z) / r mod n
    d = ((s1 * k - z1) % n * modinv(r, n)) % n
    
    return d, k

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with the same r value (nonce reuse)
    r_values = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_values:
            r_values[r] = []
        r_values[r].append(i)
    
    # Find a pair with reused nonce
    d = None
    k = None
    for r, indices in r_values.items():
        if len(indices) >= 2:
            # Found nonce reuse! Recover the key
            sig1 = signatures[indices[0]]
            sig2 = signatures[indices[1]]
            d, k = recover_key_from_nonce_reuse(sig1, sig2, n)
            break
    
    # Format output as 64 lowercase hex characters
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()