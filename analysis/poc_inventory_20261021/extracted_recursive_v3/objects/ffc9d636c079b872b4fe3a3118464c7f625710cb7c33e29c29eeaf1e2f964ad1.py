import json
import sys

def modinv(a, m):
    """Compute modular inverse of a mod m"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def recover_private_key(sigs):
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with same r (nonce reuse)
    r_to_sigs = {}
    for i, sig in enumerate(sigs):
        r = int(sig['r'], 16)
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((i, sig))
    
    # Find a pair with reused nonce
    for r, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            sig1 = sig_list[0][1]
            sig2 = sig_list[1][1]
            
            r_val = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Recover k: k = (z1 - z2) / (s1 - s2) mod n
            k = ((z1 - z2) % n) * modinv((s1 - s2) % n, n) % n
            
            # Recover d: d = (s*k - z) / r mod n
            d = ((s1 * k - z1) % n) * modinv(r_val, n) % n
            
            # Format as 64 hex characters
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            return d_hex, k_hex
    
    return None, None

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    sigs = instance['signatures']
    d_hex, k_hex = recover_private_key(sigs)
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()