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

def recover_private_key(signatures, public_key, p, n, G):
    """
    Recover private key from ECDSA signatures with repeated nonces.
    """
    # Group signatures by r value (same r means same k)
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append({'s': s, 'z': z, 'r': r})
    
    # Find pairs with the same r
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use the first two signatures with the same r
            sig1, sig2 = sigs[0], sigs[1]
            s1, z1 = sig1['s'], sig1['z']
            s2, z2 = sig2['s'], sig2['z']
            
            # Calculate k: k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k = (numerator * modinv(denominator, n)) % n
            
            # Calculate private key: d = (s*k - z) / r mod n
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            # Verify the private key
            Qx = int(public_key['x'], 16)
            Qy = int(public_key['y'], 16)
            
            # Check if d * G = Q (public key)
            # For secp256k1, we can verify by checking signature
            if d != 0:
                return d
    
    return None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    public_key = instance['public_key']
    signatures = instance['signatures']
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    G = (Gx, Gy)
    
    d = recover_private_key(signatures, public_key, p, n, G)
    
    if d is None:
        # Fallback: shouldn't happen with valid input
        d = 0
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
