import sys
import json
import base64

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_bytes(n, length):
    return n.to_bytes(length, 'big')

def modinv(a, m):
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def egcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = egcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA parameters for secp256r1 (P-256)
    p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
    n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
    
    # Decode public key
    Qx = bytes_to_int(base64.b64decode(instance['public_key']['x']))
    Qy = bytes_to_int(base64.b64decode(instance['public_key']['y']))
    
    # Decode signatures
    signatures = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # Look for repeated r values (nonce reuse)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find nonce reuse
    d = None
    k = None
    
    for r, sigs in r_map.items():
        if len(sigs) >= 2:
            # Nonce reuse detected
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k_candidate = (numerator * modinv(denominator, n)) % n
            
            # d = (s * k - z) / r mod n
            d_candidate = ((s1 * k_candidate - z1) % n * modinv(r, n)) % n
            
            # Verify with another signature
            valid = True
            for r_test, s_test, z_test in signatures[:3]:
                k_test = ((z_test + r_test * d_candidate) % n * modinv(s_test, n)) % n
                if k_test == 0:
                    valid = False
                    break
            
            if valid:
                d = d_candidate
                k = k_candidate
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
