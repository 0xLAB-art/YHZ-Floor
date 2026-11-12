import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_key_from_nonce_reuse(r1, s1, z1, r2, s2, z2, n):
    """Recover private key d and nonce k from two signatures with same nonce"""
    # k = (z1 - z2) / (s1 - s2) mod n
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # d = (s * k - z) / r mod n
    r_inv = modinv(r1, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find duplicate r values
    r_to_sigs = {}
    for idx, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((idx, sig))
    
    # Find a pair with duplicate r
    for r, sigs in r_to_sigs.items():
        if len(sigs) >= 2:
            # Use first two signatures with this r value
            idx1, sig1 = sigs[0]
            idx2, sig2 = sigs[1]
            
            r1 = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            z1 = int(sig1['z'], 16)
            
            r2 = int(sig2['r'], 16)
            s2 = int(sig2['s'], 16)
            z2 = int(sig2['z'], 16)
            
            # Recover private key and nonce
            d, k = recover_key_from_nonce_reuse(r1, s1, z1, r2, s2, z2, n)
            
            # Format as 64-character lowercase hex
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            
            print(json.dumps(result))
            return
    
    # Should not reach here if there are duplicate r values
    raise ValueError("No duplicate r values found")

if __name__ == "__main__":
    main()