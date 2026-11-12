import sys
import json
import base64


def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_bytes(n, length=32):
    return n.to_bytes(length, 'big')

def mod_inverse(a, m):
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
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
    
    # Decode public key
    pk_x = base64.b64decode(instance['public_key']['x'])
    pk_y = base64.b64decode(instance['public_key']['y'])
    
    Qx = bytes_to_int(pk_x)
    Qy = bytes_to_int(pk_y)
    
    # Secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode signatures
    signatures = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # Look for duplicate r values (nonce reuse)
    r_dict = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_dict:
            r_dict[r] = []
        r_dict[r].append((i, s, z))
    
    # Find nonce reuse and recover private key
    d = None
    k = None
    
    for r, sig_list in r_dict.items():
        if len(sig_list) >= 2:
            # We have nonce reuse!
            i1, s1, z1 = sig_list[0]
            i2, s2, z2 = sig_list[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s*k - z) / r mod n
            
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k_recovered = (numerator * mod_inverse(denominator, n)) % n
            
            # Verify k and recover d
            # s = (z + r*d) / k mod n
            # s*k = z + r*d mod n
            # d = (s*k - z) / r mod n
            
            numerator_d = (s1 * k_recovered - z1) % n
            denominator_d = r % n
            
            if denominator_d == 0:
                continue
            
            d_recovered = (numerator_d * mod_inverse(denominator_d, n)) % n
            
            # Verify this is correct by checking if d*G = Q
            # We can verify with the signature equation instead
            # Let's verify with the second signature
            expected_s = ((z2 + r * d_recovered) * mod_inverse(k_recovered, n)) % n
            
            if expected_s == s2:
                d = d_recovered
                k = k_recovered
                break
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
