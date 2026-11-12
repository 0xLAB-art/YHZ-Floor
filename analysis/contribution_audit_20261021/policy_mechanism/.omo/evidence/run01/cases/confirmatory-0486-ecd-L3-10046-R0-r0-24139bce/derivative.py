import sys
import json


def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_key_from_duplicate_nonce(sig1, sig2, n):
    """
    Given two signatures with the same k (same r), recover k and d.
    
    For ECDSA:
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    From these:
    s1 - s2 = k^-1 * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    
    Then:
    d = (s*k - z) / r mod n
    """
    r = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Calculate k
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    
    k = (z_diff * modinv(s_diff, n)) % n
    
    # Calculate d using first signature
    d = (((s1 * k - z1) % n) * modinv(r, n)) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # secp256k1 order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = data['signatures']
    
    # Find duplicate r values
    r_to_sigs = {}
    for sig in signatures:
        r = sig['r']
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append(sig)
    
    # Find a pair with duplicate r
    for r, sigs in r_to_sigs.items():
        if len(sigs) >= 2:
            # Use the first two signatures with the same r
            d, k = recover_key_from_duplicate_nonce(sigs[0], sigs[1], n)
            
            # Format output
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
