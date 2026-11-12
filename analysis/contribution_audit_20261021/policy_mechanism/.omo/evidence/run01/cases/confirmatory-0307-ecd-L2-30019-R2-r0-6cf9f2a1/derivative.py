import sys
import json
import base64


def mod_inverse(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        return None
    return (x % m + m) % m

def recover_private_key(signatures, n):
    """
    Recover private key from signatures with repeated r or nonce reuse.
    If two signatures share the same r, we can recover k and then d.
    """
    # Group signatures by r value
    r_groups = {}
    for sig in signatures:
        r = sig['r']
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(sig)
    
    # Find r values that appear more than once
    for r_val, sigs in r_groups.items():
        if len(sigs) >= 2:
            # We have nonce reuse! Use first two signatures with same r
            sig1, sig2 = sigs[0], sigs[1]
            
            r = sig1['r']
            s1 = sig1['s']
            s2 = sig2['s']
            z1 = sig1['z']
            z2 = sig2['z']
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s1 * k - z1) / r mod n
            
            z_diff = (z1 - z2) % n
            s_diff = (s1 - s2) % n
            
            s_diff_inv = mod_inverse(s_diff, n)
            if s_diff_inv is None:
                continue
                
            k = (z_diff * s_diff_inv) % n
            
            # Now recover d from: s = k^-1 * (z + r*d) mod n
            # => s*k = z + r*d mod n
            # => d = (s*k - z) / r mod n
            
            r_inv = mod_inverse(r, n)
            if r_inv is None:
                continue
            
            d = ((s1 * k - z1) * r_inv) % n
            
            return d
    
    return None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA parameters for secp256r1 (P-256)
    p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Decode public key
    pub_x = int.from_bytes(base64.b64decode(instance['public_key']['x']), 'big')
    pub_y = int.from_bytes(base64.b64decode(instance['public_key']['y']), 'big')
    
    # Decode signatures
    signatures = []
    for sig in instance['signatures']:
        r = int.from_bytes(base64.b64decode(sig['r']), 'big')
        s = int.from_bytes(base64.b64decode(sig['s']), 'big')
        z = int.from_bytes(base64.b64decode(sig['z']), 'big')
        signatures.append({'r': r, 's': s, 'z': z})
    
    # Try to recover private key
    d = recover_private_key(signatures, n)
    
    if d is None:
        d = 0
    
    # Format output
    d_hex = format(d, '064x')
    
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
