import json
import sys
import base64


def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

def mod_inverse(a, m):
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    signatures = []
    for sig in data['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # Find duplicate r values
    r_to_sigs = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((s, z, i))
    
    # Find a pair with the same r
    d = None
    k = None
    
    for r, sigs in r_to_sigs.items():
        if len(sigs) >= 2:
            s1, z1, _ = sigs[0]
            s2, z2, _ = sigs[1]
            
            # Recover k from the pair
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            s_diff_inv = mod_inverse(s_diff, n)
            k_candidate = (z_diff * s_diff_inv) % n
            
            # Recover d from k
            k_inv = mod_inverse(k_candidate, n)
            r_inv = mod_inverse(r, n)
            d_candidate = ((s1 * k_candidate - z1) * r_inv) % n
            
            k = k_candidate
            d = d_candidate
            break
    
    result = {
        "d": int_to_hex(d),
        "k": int_to_hex(k)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
