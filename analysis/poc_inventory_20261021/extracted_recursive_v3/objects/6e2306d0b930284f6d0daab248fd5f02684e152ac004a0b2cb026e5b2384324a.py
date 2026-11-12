import json
import sys

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
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

def recover_key_from_nonce_reuse(r, s1, z1, s2, z2, n):
    """Recover private key d and nonce k from two signatures with same r."""
    # k = (z1 - z2) / (s1 - s2) mod n
    k = ((z1 - z2) * modinv(s1 - s2, n)) % n
    
    # d = (s * k - z) / r mod n
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Find signatures with the same r value
    r_map = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((s, z))
    
    # Find a repeated r value
    for r, sig_list in r_map.items():
        if len(sig_list) >= 2:
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            # Recover the private key
            d, k = recover_key_from_nonce_reuse(r, s1, z1, s2, z2, n)
            
            # Format as 64 lowercase hex characters
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            
            print(json.dumps(result))
            return
    
    # Should not reach here if there's nonce reuse
    raise ValueError("No nonce reuse found")

if __name__ == "__main__":
    main()