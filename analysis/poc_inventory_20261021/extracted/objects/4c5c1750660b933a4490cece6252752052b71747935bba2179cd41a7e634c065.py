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

def recover_private_key(signatures, n):
    """
    Recover private key from ECDSA signatures with nonce reuse.
    If two signatures share the same r value, they used the same nonce k.
    Given: s1 = k^-1 * (z1 + r*d) mod n
           s2 = k^-1 * (z2 + r*d) mod n
    We can solve for k and d.
    """
    # Find duplicate r values
    r_to_sigs = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((s, z))
    
    # Find pairs with same r
    for r, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            # Use first two signatures with same r
            s1, z1 = sig_list[0]
            s2, z2 = sig_list[1]
            
            # Calculate k from the two signatures
            # s1 - s2 = k^-1 * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
            
            k = (z_diff * modinv(s_diff, n)) % n
            
            if k == 0:
                continue
            
            # Now recover d from one of the signatures
            # s1 = k^-1 * (z1 + r*d) mod n
            # s1 * k = z1 + r*d mod n
            # d = (s1 * k - z1) / r mod n
            
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            # Return both values as 64 character hex strings
            k_hex = format(k, '064x')
            d_hex = format(d, '064x')
            
            return d_hex, k_hex
    
    return None, None

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    d_hex, k_hex = recover_private_key(signatures, n)
    
    # Output result
    result = {
        "d": d_hex,
        "k": k_hex
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
