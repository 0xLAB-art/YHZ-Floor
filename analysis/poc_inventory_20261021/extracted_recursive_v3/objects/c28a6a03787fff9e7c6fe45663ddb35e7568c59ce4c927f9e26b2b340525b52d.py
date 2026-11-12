import json
import sys
import hashlib

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def recover_key_from_reused_nonce(r, s1, s2, z1, z2, n):
    """Recover private key from two signatures with same nonce"""
    # k = (z1 - z2) / (s1 - s2) mod n
    k = ((z1 - z2) * modinv(s1 - s2, n)) % n
    
    # d = (s*k - z) / r mod n
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return d, k

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Find signatures with same r value (nonce reuse)
    r_map = {}
    for idx, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(idx)
    
    # Find reused nonce
    for r, indices in r_map.items():
        if len(indices) >= 2:
            idx1, idx2 = indices[0], indices[1]
            sig1 = signatures[idx1]
            sig2 = signatures[idx2]
            
            r_val = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            d, k = recover_key_from_reused_nonce(r_val, s1, s2, z1, z2, n)
            
            # Format as 64 character hex strings
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            print(json.dumps({"d": d_hex, "k": k_hex}))
            return

if __name__ == "__main__":
    main()
