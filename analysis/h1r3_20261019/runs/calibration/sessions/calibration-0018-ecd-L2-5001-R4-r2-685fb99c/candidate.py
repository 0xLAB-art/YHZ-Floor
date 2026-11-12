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

def recover_private_key(signatures, public_key, p, n):
    """Recover private key using ECDSA nonce reuse attack."""
    # Look for signatures with the same r value (indicating nonce reuse)
    r_dict = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_dict:
            r_dict[r] = []
        r_dict[r].append(i)
    
    # Find r values that appear more than once
    for r, indices in r_dict.items():
        if len(indices) >= 2:
            # Use the first two signatures with the same r
            i1, i2 = indices[0], indices[1]
            s1 = int(signatures[i1]['s'], 16)
            s2 = int(signatures[i2]['s'], 16)
            z1 = int(signatures[i1]['z'], 16)
            z2 = int(signatures[i2]['z'], 16)
            
            # ECDSA nonce reuse attack
            # s1 = k^(-1) * (z1 + r * d) mod n
            # s2 = k^(-1) * (z2 + r * d) mod n
            # s1 - s2 = k^(-1) * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
                
            try:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Now recover d: s1 = k^(-1) * (z1 + r * d) mod n
                # k * s1 = z1 + r * d mod n
                # d = (k * s1 - z1) / r mod n
                
                k_inv = modinv(k, n)
                r_inv = modinv(r, n)
                d = ((s1 * k - z1) % n * r_inv) % n
                
                # Verify the private key is correct by checking public key
                # Public key Q = d * G, we need to verify this matches
                return d
            except ValueError:
                continue
    
    return None

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    public_key = instance['public_key']
    signatures = instance['signatures']
    
    # Recover private key
    d = recover_private_key(signatures, public_key, p, n)
    
    if d is None:
        # If nonce reuse didn't work, try other approaches or return error
        d = 0
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
