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

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    Qx = int(instance['public_key']['x'], 16)
    Qy = int(instance['public_key']['y'], 16)
    
    # Parse signatures
    sigs = instance['signatures']
    
    # We have two signatures with the same r value (nonce reuse)
    r1 = int(sigs[0]['r'], 16)
    s1 = int(sigs[0]['s'], 16)
    z1 = int(sigs[0]['z'], 16)
    
    r2 = int(sigs[1]['r'], 16)
    s2 = int(sigs[1]['s'], 16)
    z2 = int(sigs[1]['z'], 16)
    
    # Verify that r values are the same (nonce reuse attack)
    assert r1 == r2, "r values must be the same for nonce reuse attack"
    
    # ECDSA nonce reuse attack
    # s1 = k^(-1) * (z1 + r * d) mod n
    # s2 = k^(-1) * (z2 + r * d) mod n
    # 
    # s1 - s2 = k^(-1) * (z1 - z2) mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    # 
    # Then: d = (s * k - z) / r mod n
    
    # Calculate k (the nonce)
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate private key d using first signature
    r_inv = modinv(r1, n)
    d = (r_inv * (s1 * k - z1)) % n
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output result
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()