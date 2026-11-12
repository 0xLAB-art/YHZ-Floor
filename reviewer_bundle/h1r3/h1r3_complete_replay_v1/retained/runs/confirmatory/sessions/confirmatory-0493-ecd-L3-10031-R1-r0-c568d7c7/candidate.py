import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
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
    """Recover private key when same nonce k is used for two signatures."""
    # k = (z1 - z2) / (s1 - s2) mod n
    # d = (s*k - z) / r mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    try:
        s_diff_inv = modinv(s_diff, n)
        k = (z_diff * s_diff_inv) % n
        
        # Recover private key d
        r_inv = modinv(r, n)
        d = (((s1 * k - z1) % n) * r_inv) % n
        
        return d, k
    except:
        return None, None

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
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sigs.append((r, s, z))
    
    # Look for signatures with the same r value (indicating nonce reuse)
    r_map = {}
    for i, (r, s, z) in enumerate(sigs):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find nonce reuse
    d = None
    k = None
    
    for r, sig_list in r_map.items():
        if len(sig_list) >= 2:
            # Found nonce reuse
            idx1, s1, z1 = sig_list[0]
            idx2, s2, z2 = sig_list[1]
            
            d, k = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
            
            if d is not None:
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
