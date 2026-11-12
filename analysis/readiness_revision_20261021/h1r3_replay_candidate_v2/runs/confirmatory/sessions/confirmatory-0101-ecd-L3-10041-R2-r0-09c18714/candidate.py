import sys
import json
import base64

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_bytes(n, length):
    return n.to_bytes(length, 'big')

def mod_inverse(a, m):
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode public key
    x_bytes = base64.b64decode(instance['public_key']['x'])
    y_bytes = base64.b64decode(instance['public_key']['y'])
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode signatures
    signatures = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # Find duplicate r values (nonce reuse)
    r_dict = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_dict:
            r_dict[r] = []
        r_dict[r].append((i, s, z))
    
    # Look for nonce reuse
    d = None
    k = None
    
    for r, sigs in r_dict.items():
        if len(sigs) >= 2:
            # Nonce reuse detected
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator != 0:
                k = (numerator * mod_inverse(denominator, n)) % n
                
                # d = (s * k - z) / r mod n
                d = ((s1 * k - z1) % n * mod_inverse(r, n)) % n
                break
    
    if d is None:
        # Fallback: shouldn't happen with nonce reuse
        d = 0
        k = 0
    
    # Convert to hex
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
