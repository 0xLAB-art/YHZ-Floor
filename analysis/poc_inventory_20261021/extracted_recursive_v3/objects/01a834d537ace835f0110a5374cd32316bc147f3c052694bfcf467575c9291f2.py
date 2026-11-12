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
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def recover_private_key(r1, s1, z1, r2, s2, z2, n):
    """Recover private key from two signatures with same nonce"""
    # k = (z1 - z2) / (s1 - s2) mod n
    k = ((z1 - z2) % n) * modinv((s1 - s2) % n, n) % n
    
    # d = (s*k - z) / r mod n
    d = ((s1 * k - z1) % n) * modinv(r1, n) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Convert signatures to integers
    sigs = []
    for sig in signatures:
        sigs.append({
            'r': int(sig['r'], 16),
            's': int(sig['s'], 16),
            'z': int(sig['z'], 16)
        })
    
    # Find signatures with same r (same nonce)
    for i in range(len(sigs)):
        for j in range(i + 1, len(sigs)):
            if sigs[i]['r'] == sigs[j]['r']:
                # Found two signatures with same nonce
                d = recover_private_key(
                    sigs[i]['r'], sigs[i]['s'], sigs[i]['z'],
                    sigs[j]['r'], sigs[j]['s'], sigs[j]['z'],
                    n
                )
                
                # Output result
                result = {'d': format(d, '064x')}
                print(json.dumps(result))
                return
    
    # If no match found, something is wrong
    raise ValueError("No signatures with matching r found")

if __name__ == '__main__':
    main()