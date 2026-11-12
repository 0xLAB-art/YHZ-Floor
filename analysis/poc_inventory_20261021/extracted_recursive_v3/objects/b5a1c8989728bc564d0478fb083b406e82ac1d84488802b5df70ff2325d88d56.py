import json
import sys

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

def recover_private_key_from_repeated_k(sig1, sig2, n):
    """
    Recover private key when the same k (nonce) is used in two signatures.
    
    ECDSA signature equations:
    r = (k * G).x mod n
    s = k^(-1) * (z + r * d) mod n
    
    When k is reused (r1 == r2):
    s1 = k^(-1) * (z1 + r * d) mod n
    s2 = k^(-1) * (z2 + r * d) mod n
    
    Therefore:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s * k - z) / r mod n
    """
    r1, s1, z1 = sig1
    r2, s2, z2 = sig2
    
    if r1 != r2:
        return None
    
    r = r1
    
    # Calculate k = (z1 - z2) / (s1 - s2) mod n
    delta_z = (z1 - z2) % n
    delta_s = (s1 - s2) % n
    
    if delta_s == 0:
        return None
    
    k = (delta_z * modinv(delta_s, n)) % n
    
    # Calculate d = (s * k - z) / r mod n
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # SECP256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    signatures = []
    for sig in data['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # Look for repeated r values (indicating k reuse)
    d = None
    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            d = recover_private_key_from_repeated_k(signatures[i], signatures[j], n)
            if d is not None:
                break
        if d is not None:
            break
    
    # Format output
    d_hex = format(d, '064x')
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()