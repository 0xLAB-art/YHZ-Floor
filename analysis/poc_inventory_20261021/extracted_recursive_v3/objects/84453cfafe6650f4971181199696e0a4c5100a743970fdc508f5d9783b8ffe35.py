import sys
import json
import hashlib

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key_from_reused_nonce(r, s1, z1, s2, z2, n):
    """Recover private key when same nonce k is used for two signatures"""
    # k = (z1 - z2) / (s1 - s2) mod n
    # d = (s*k - z) / r mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    k = (z_diff * modinv(s_diff, n)) % n
    
    # Compute private key d
    d = (((s1 * k - z1) % n) * modinv(r, n)) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Parse signatures
    sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sigs.append((r, s, z))
    
    # Look for duplicate r values (same nonce k)
    r_to_sigs = {}
    for i, (r, s, z) in enumerate(sigs):
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((i, s, z))
    
    # Find duplicate r values
    d = None
    k = None
    
    for r, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            # Found reused nonce!
            i1, s1, z1 = sig_list[0]
            i2, s2, z2 = sig_list[1]
            
            try:
                d, k = recover_private_key_from_reused_nonce(r, s1, z1, s2, z2, n)
                break
            except:
                continue
    
    if d is None:
        # No duplicate r found, this shouldn't happen for this challenge
        raise Exception("No nonce reuse detected")
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()