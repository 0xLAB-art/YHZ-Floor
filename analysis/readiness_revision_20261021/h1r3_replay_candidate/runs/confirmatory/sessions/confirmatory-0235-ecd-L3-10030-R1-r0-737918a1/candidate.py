import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with same r value
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find pair with same r
    for r_val, indices in r_map.items():
        if len(indices) >= 2:
            i1, i2 = indices[0], indices[1]
            sig1 = signatures[i1]
            sig2 = signatures[i2]
            
            r = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            z1 = int(sig1['z'], 16)
            s2 = int(sig2['s'], 16)
            z2 = int(sig2['z'], 16)
            
            # Calculate k = (z1 - z2) / (s1 - s2) mod n
            z_diff = (z1 - z2) % n
            s_diff = (s1 - s2) % n
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Calculate d = (s*k - z) / r mod n
            r_inv = modinv(r, n)
            d = ((s1 * k - z1) * r_inv) % n
            
            # Format as 64 character hex strings
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            
            print(json.dumps(result))
            return
    
    # If no matching r found, should not happen with this instance
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()
