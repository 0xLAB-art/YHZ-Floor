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

def recover_private_key_from_repeated_k(r1, s1, z1, r2, s2, z2, n):
    """
    Recover private key when the same k (nonce) is used in two signatures.
    
    For ECDSA signatures with the same k:
    s1 = k^(-1) * (z1 + r * d) mod n
    s2 = k^(-1) * (z2 + r * d) mod n
    
    From these we can derive:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s * k - z) / r mod n
    """
    # Calculate k from the two signatures
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate private key d from k
    r_inv = modinv(r1, n)
    d = (r_inv * (s1 * k - z1)) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sigs.append((r, s, z))
    
    # Find signatures with the same r value (indicating same k)
    r_to_sigs = {}
    for i, (r, s, z) in enumerate(sigs):
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((i, s, z))
    
    # Find a pair with repeated r
    d = None
    k = None
    for r, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            # We have at least two signatures with the same r (same k)
            i1, s1, z1 = sig_list[0]
            i2, s2, z2 = sig_list[1]
            
            try:
                d, k = recover_private_key_from_repeated_k(r, s1, z1, r, s2, z2, n)
                break
            except:
                continue
    
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
