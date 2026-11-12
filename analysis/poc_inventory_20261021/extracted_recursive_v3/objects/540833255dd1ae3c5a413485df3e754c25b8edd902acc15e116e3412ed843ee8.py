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

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Extract public key
    Qx = int(instance['public_key']['x'], 16)
    Qy = int(instance['public_key']['y'], 16)
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    
    signatures = instance['signatures']
    
    # Look for repeated r values (nonce reuse attack)
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r in r_map:
            # Found duplicate r! Extract private key
            j = r_map[r]
            
            r1 = int(signatures[j]['r'], 16)
            s1 = int(signatures[j]['s'], 16)
            z1 = int(signatures[j]['z'], 16)
            
            r2 = int(signatures[i]['r'], 16)
            s2 = int(signatures[i]['s'], 16)
            z2 = int(signatures[i]['z'], 16)
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s1 * k - z1) / r1 mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Extract private key d
            d = ((s1 * k - z1) * modinv(r1, n)) % n
            
            # Format output
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            
            print(json.dumps(result))
            return
        
        r_map[r] = i
    
    # Should not reach here if instance is solvable
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()