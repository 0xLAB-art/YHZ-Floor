import json
import sys

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
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
        data = json.load(f)
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    Qx = int(data['public_key']['x'], 16)
    Qy = int(data['public_key']['y'], 16)
    
    # Parse signatures
    signatures = []
    for sig in data['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # Look for duplicate r values (nonce reuse)
    r_dict = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_dict:
            # Found duplicate r - nonce reuse attack
            j = r_dict[r]
            r1, s1, z1 = signatures[j]
            r2, s2, z2 = signatures[i]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s * k - z) / r mod n
            
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            k = (numerator * modinv(denominator, n)) % n
            
            # Recover private key d
            d = ((s1 * k - z1) * modinv(r1, n)) % n
            
            # Verify with the other signature
            d_check = ((s2 * k - z2) * modinv(r2, n)) % n
            
            if d == d_check:
                # Format output
                result = {
                    "d": format(d, '064x'),
                    "k": format(k, '064x')
                }
                print(json.dumps(result))
                return
        else:
            r_dict[r] = i
    
    # If no solution found, output zeros (shouldn't happen with valid input)
    result = {
        "d": "0" * 64,
        "k": "0" * 64
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
