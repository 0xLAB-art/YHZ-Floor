import sys
import json

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = egcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = egcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def recover_private_key(sigs):
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with same r (reused nonce)
    r_map = {}
    for i, sig in enumerate(sigs):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find a pair with same r
    for r_val, indices in r_map.items():
        if len(indices) >= 2:
            i1, i2 = indices[0], indices[1]
            sig1 = sigs[i1]
            sig2 = sigs[i2]
            
            r = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Recover k from the two signatures
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Recover private key d
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            return d
    
    return None

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    sigs = instance['signatures']
    d = recover_private_key(sigs)
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    print(json.dumps({"d": d_hex}))

if __name__ == '__main__':
    main()