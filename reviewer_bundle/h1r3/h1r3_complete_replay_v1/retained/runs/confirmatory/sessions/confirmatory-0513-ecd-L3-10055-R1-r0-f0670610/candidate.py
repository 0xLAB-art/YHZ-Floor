import sys
import json
import hashlib

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

def recover_key_from_duplicate_nonce(sig1, sig2, n):
    """Recover private key from two signatures with same nonce (same r value)."""
    r1 = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    
    r2 = int(sig2['r'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Both signatures should have same r
    assert r1 == r2, "r values must match"
    r = r1
    
    # Recover k: k = (z1 - z2) / (s1 - s2) mod n
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    
    if s_diff == 0:
        return None
    
    k = (z_diff * modinv(s_diff, n)) % n
    
    # Recover d: d = (s*k - z) / r mod n
    d = ((s1 * k - z1) % n * modinv(r, n)) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find duplicate r values
    r_to_sigs = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((i, sig))
    
    # Find pairs with duplicate r
    d = None
    k = None
    
    for r_val, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            # Found duplicate r - exploit it
            sig1 = sig_list[0][1]
            sig2 = sig_list[1][1]
            
            result = recover_key_from_duplicate_nonce(sig1, sig2, n)
            if result:
                d, k = result
                break
    
    if d is None:
        raise ValueError("Could not recover private key")
    
    # Format as 64 hex characters (lowercase, zero-padded)
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    # Output result
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
