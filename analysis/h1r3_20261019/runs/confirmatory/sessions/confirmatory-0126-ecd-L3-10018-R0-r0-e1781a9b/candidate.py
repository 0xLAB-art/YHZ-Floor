import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n):
    """
    Recover private key k (the nonce) when the same nonce is used twice.
    From ECDSA: s = k^(-1) * (z + r*d) mod n
    If same k (nonce) is used: s1 = k^(-1) * (z1 + r*d), s2 = k^(-1) * (z2 + r*d)
    Then: k = (z1 - z2) / (s1 - s2) mod n
    And: d = (s1*k - z1) / r mod n
    """
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d, k

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Look for nonce reuse - same r value in multiple signatures
    r_map = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((s, z))
    
    # Find r values that appear more than once
    for r, sig_list in r_map.items():
        if len(sig_list) >= 2:
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            try:
                d, k = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
                
                # Format as 64 lowercase hex characters
                d_hex = format(d, '064x')
                k_hex = format(k, '064x')
                
                result = {
                    "d": d_hex,
                    "k": k_hex
                }
                
                print(json.dumps(result))
                return
            except:
                continue
    
    # If no solution found, output zeros (shouldn't happen with valid input)
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()
