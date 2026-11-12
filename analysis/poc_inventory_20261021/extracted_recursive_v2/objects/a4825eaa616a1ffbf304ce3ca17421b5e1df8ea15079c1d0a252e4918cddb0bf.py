import json
import sys

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def recover_key_from_nonce_reuse(r, s1, z1, s2, z2, n):
    """Recover private key when same nonce is used for two signatures"""
    # Calculate k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # Calculate d = (s1 * k - z1) / r mod n
    numerator = (s1 * k - z1) % n
    d = (numerator * modinv(r, n)) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Convert hex to integers
    sigs = []
    for sig in signatures:
        sigs.append({
            'r': int(sig['r'], 16),
            's': int(sig['s'], 16),
            'z': int(sig['z'], 16)
        })
    
    # Find signatures with same r value (nonce reuse)
    r_map = {}
    for i, sig in enumerate(sigs):
        r = sig['r']
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find reused nonces
    for r, indices in r_map.items():
        if len(indices) >= 2:
            # Found nonce reuse
            i1, i2 = indices[0], indices[1]
            sig1, sig2 = sigs[i1], sigs[i2]
            
            d, k = recover_key_from_nonce_reuse(
                r, 
                sig1['s'], sig1['z'],
                sig2['s'], sig2['z'],
                n
            )
            
            # Format as 64-character lowercase hex
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            
            print(json.dumps(result))
            return

if __name__ == '__main__':
    main()
