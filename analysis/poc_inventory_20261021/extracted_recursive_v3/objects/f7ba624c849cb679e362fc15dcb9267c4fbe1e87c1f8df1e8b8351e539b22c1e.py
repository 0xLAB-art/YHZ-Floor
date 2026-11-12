import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm"""
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

def recover_private_key(sig1, sig2, n):
    """Recover private key from two signatures with same nonce"""
    r1 = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    
    r2 = int(sig2['r'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Verify same r value
    if r1 != r2:
        return None
    
    r = r1
    
    # Calculate k = (z1 - z2) / (s1 - s2) mod n
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    
    if s_diff == 0:
        return None
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d = (s*k - z) / r mod n
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with duplicate r values
    r_to_indices = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_to_indices:
            r_to_indices[r] = []
        r_to_indices[r].append(i)
    
    # Find duplicate r values
    d = None
    k = None
    for r_val, indices in r_to_indices.items():
        if len(indices) >= 2:
            # Found duplicate r, recover key
            result = recover_private_key(signatures[indices[0]], signatures[indices[1]], n)
            if result:
                d, k = result
                break
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    output = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(output))

if __name__ == '__main__':
    main()