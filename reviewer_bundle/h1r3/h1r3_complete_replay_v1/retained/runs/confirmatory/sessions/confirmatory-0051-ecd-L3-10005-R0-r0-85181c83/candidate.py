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

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Find duplicate r values
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find a pair with same r
    for r, indices in r_map.items():
        if len(indices) >= 2:
            # Use first two signatures with same r
            i1, i2 = indices[0], indices[1]
            sig1 = signatures[i1]
            sig2 = signatures[i2]
            
            r = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            z1 = int(sig1['z'], 16)
            s2 = int(sig2['s'], 16)
            z2 = int(sig2['z'], 16)
            
            # Recover k (nonce)
            # k = (z1 - z2) * (s1 - s2)^(-1) mod n
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Recover d (private key)
            # s1 = k^(-1) * (z1 + r*d) mod n
            # s1 * k = z1 + r*d mod n
            # d = (s1*k - z1) * r^(-1) mod n
            r_inv = modinv(r, n)
            d = ((s1 * k - z1) % n * r_inv) % n
            
            # Format output
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            
            print(json.dumps(result))
            return

if __name__ == "__main__":
    main()
