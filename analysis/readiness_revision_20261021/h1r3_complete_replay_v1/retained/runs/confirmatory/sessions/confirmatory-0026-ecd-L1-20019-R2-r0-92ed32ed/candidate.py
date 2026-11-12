import json
import sys
import base64
import hashlib

def decode_base64(s):
    return int.from_bytes(base64.b64decode(s), 'big')

def modinv(a, m):
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
    
    # Decode public key
    pub_x = decode_base64(instance['public_key']['x'])
    pub_y = decode_base64(instance['public_key']['y'])
    
    # Decode signatures
    sigs = []
    for sig in instance['signatures']:
        r = decode_base64(sig['r'])
        s = decode_base64(sig['s'])
        z = decode_base64(sig['z'])
        sigs.append({'r': r, 's': s, 'z': z})
    
    # ECDSA is over secp256k1
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Two signatures with same r but different s and z
    # This is a nonce reuse attack
    r = sigs[0]['r']
    s1 = sigs[0]['s']
    z1 = sigs[0]['z']
    s2 = sigs[1]['s']
    z2 = sigs[1]['z']
    
    # From ECDSA: s = k^(-1) * (z + r*d) mod n
    # s1 = k^(-1) * (z1 + r*d) mod n
    # s2 = k^(-1) * (z2 + r*d) mod n
    # s1 - s2 = k^(-1) * (z1 - z2) mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    k = (z_diff * modinv(s_diff, n)) % n
    
    # Now recover private key d
    # s1 = k^(-1) * (z1 + r*d) mod n
    # s1 * k = z1 + r*d mod n
    # d = (s1*k - z1) / r mod n
    
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
