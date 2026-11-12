import sys
import json
import base64
from typing import List, Tuple

def bytes_to_int(b: bytes) -> int:
    return int.from_bytes(b, 'big')

def int_to_hex(n: int) -> str:
    return format(n, '064x')

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(a: int, m: int) -> int:
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    # ECDSA parameters for secp256k1
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode public key
    pub_x = bytes_to_int(base64.b64decode(data['public_key']['x']))
    pub_y = bytes_to_int(base64.b64decode(data['public_key']['y']))
    
    # Decode signatures
    signatures = []
    for sig in data['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # Look for nonce reuse (same r value)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find duplicate r values
    private_key = None
    for r, sigs in r_map.items():
        if len(sigs) >= 2:
            # Nonce reuse detected
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            # Calculate k (nonce)
            # k = (z1 - z2) / (s1 - s2) mod n
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator != 0:
                k = (numerator * mod_inverse(denominator, n)) % n
                
                # Calculate private key d
                # d = (s1 * k - z1) / r mod n
                d = ((s1 * k - z1) * mod_inverse(r, n)) % n
                
                private_key = d
                nonce = k
                break
    
    if private_key is None:
        # Fallback (shouldn't happen with nonce reuse)
        private_key = 0
        nonce = 0
    
    result = {
        "d": int_to_hex(private_key),
        "k": int_to_hex(nonce)
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()