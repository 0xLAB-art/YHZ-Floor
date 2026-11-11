import json
import sys

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def recover_private_key(r1, s1, z1, r2, s2, z2, n):
    """Recover private key from two signatures with same r value"""
    # Both signatures use the same r, so r1 == r2
    r = r1
    
    # Calculate k = (z1 - z2) / (s1 - s2) mod n
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d = (s*k - z) / r mod n
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find two signatures with the same r value
    r_to_sigs = {}
    for idx, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append(idx)
    
    # Find a pair with same r
    for r, indices in r_to_sigs.items():
        if len(indices) >= 2:
            idx1, idx2 = indices[0], indices[1]
            sig1 = signatures[idx1]
            sig2 = signatures[idx2]
            
            r1 = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            z1 = int(sig1['z'], 16)
            
            r2 = int(sig2['r'], 16)
            s2 = int(sig2['s'], 16)
            z2 = int(sig2['z'], 16)
            
            # Recover private key
            d = recover_private_key(r1, s1, z1, r2, s2, z2, n)
            
            # Format as 64 lowercase hex characters
            d_hex = format(d, '064x')
            
            # Output result
            result = {"d": d_hex}
            print(json.dumps(result))
            return
    
    # Should not reach here if instance is valid
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()
