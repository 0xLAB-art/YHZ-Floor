import sys
import json
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
        instance = json.load(f)
    
    # secp256k1 order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    sigs = instance['signatures']
    
    # Find duplicate r values
    r_map = {}
    for i, sig in enumerate(sigs):
        r_bytes = base64.b64decode(sig['r'])
        r = bytes_to_int(r_bytes)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find a pair with duplicate r
    for r, indices in r_map.items():
        if len(indices) >= 2:
            i1, i2 = indices[0], indices[1]
            
            s1 = bytes_to_int(base64.b64decode(sigs[i1]['s']))
            z1 = bytes_to_int(base64.b64decode(sigs[i1]['z']))
            s2 = bytes_to_int(base64.b64decode(sigs[i2]['s']))
            z2 = bytes_to_int(base64.b64decode(sigs[i2]['z']))
            
            # Recover k: k = (z1 - z2) / (s1 - s2) mod n
            z_diff = (z1 - z2) % n
            s_diff = (s1 - s2) % n
            s_diff_inv = mod_inverse(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Recover d: d = (s*k - z) / r mod n
            r_inv = mod_inverse(r, n)
            d = (r_inv * (s1 * k - z1)) % n
            
            result = {
                "d": int_to_hex(d),
                "k": int_to_hex(k)
            }
            print(json.dumps(result))
            return

if __name__ == '__main__':
    main()