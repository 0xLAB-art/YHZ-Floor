import json
import sys
import base64
from collections import defaultdict

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # Decode public key
    x = bytes_to_int(base64.b64decode(data['public_key']['x']))
    y = bytes_to_int(base64.b64decode(data['public_key']['y']))
    
    # Decode signatures
    signatures = []
    for sig in data['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # ECDSA uses secp256k1 curve
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Look for duplicate r values (nonce reuse)
    r_groups = defaultdict(list)
    for i, (r, s, z) in enumerate(signatures):
        r_groups[r].append((i, s, z))
    
    # Find nonce reuse
    k = None
    d = None
    
    for r, group in r_groups.items():
        if len(group) >= 2:
            # Nonce reuse found
            i1, s1, z1 = group[0]
            i2, s2, z2 = group[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            # Modular inverse
            k = (numerator * pow(denominator, -1, n)) % n
            
            # d = (s * k - z) / r mod n
            d = ((s1 * k - z1) % n * pow(r, -1, n)) % n
            
            break
    
    result = {
        "d": int_to_hex(d),
        "k": int_to_hex(k)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
