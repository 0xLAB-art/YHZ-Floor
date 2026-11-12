import json
import sys

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(sig1, sig2, n):
    """Recover private key when two signatures share the same r value"""
    r1, s1, z1 = sig1
    r2, s2, z2 = sig2
    
    # Check if r values match
    if r1 != r2:
        return None
    
    r = r1
    
    # Calculate k using: k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    denom_inv = modinv(denominator, n)
    if denom_inv is None:
        return None
    
    k = (numerator * denom_inv) % n
    
    # Calculate d using: d = (s*k - z) / r mod n
    r_inv = modinv(r, n)
    if r_inv is None:
        return None
    
    d = (((s1 * k - z1) % n) * r_inv) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # Look for duplicate r values
    d = None
    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            candidate_d = recover_private_key(signatures[i], signatures[j], n)
            if candidate_d is not None:
                d = candidate_d
                break
        if d is not None:
            break
    
    # Format output
    d_hex = format(d, '064x')
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
