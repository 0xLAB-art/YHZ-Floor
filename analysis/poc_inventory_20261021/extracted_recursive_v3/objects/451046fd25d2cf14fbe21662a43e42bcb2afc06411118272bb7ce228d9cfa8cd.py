import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(r, s1, z1, s2, z2, n):
    """Recover private key from two signatures with same nonce"""
    # Calculate k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    k = (numerator * modinv(denominator, n)) % n
    
    # Calculate d = (s * k - z) / r mod n
    numerator = (s1 * k - z1) % n
    d = (numerator * modinv(r, n)) % n
    
    return d, k

def main():
    # Read instance from command line argument
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
    
    # Find a pair with duplicate r
    for r, indices in r_map.items():
        if len(indices) >= 2:
            # Use first two signatures with this r value
            i1, i2 = indices[0], indices[1]
            sig1 = signatures[i1]
            sig2 = signatures[i2]
            
            r_val = r
            s1 = int(sig1['s'], 16)
            z1 = int(sig1['z'], 16)
            s2 = int(sig2['s'], 16)
            z2 = int(sig2['z'], 16)
            
            # Recover private key
            d, k = recover_private_key(r_val, s1, z1, s2, z2, n)
            
            # Format output
            result = {
                "d": format(d, '064x'),
                "k": format(k, '064x')
            }
            
            print(json.dumps(result))
            return
    
    # Should not reach here if instance is valid
    raise ValueError("No duplicate r values found")

if __name__ == "__main__":
    main()