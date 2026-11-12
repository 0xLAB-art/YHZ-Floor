import sys
import json
import base64
import hashlib

def modinv(a, m):
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = egcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = egcd(a % m, m)
    if gcd != 1:
        return None
    return (x % m + m) % m

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode public key
    x = int.from_bytes(base64.b64decode(instance['public_key']['x']), 'big')
    y = int.from_bytes(base64.b64decode(instance['public_key']['y']), 'big')
    
    # Decode signatures
    sigs = []
    for sig in instance['signatures']:
        r = int.from_bytes(base64.b64decode(sig['r']), 'big')
        s = int.from_bytes(base64.b64decode(sig['s']), 'big')
        z = int.from_bytes(base64.b64decode(sig['z']), 'big')
        sigs.append({'r': r, 's': s, 'z': z})
    
    # ECDSA curve order (secp256k1)
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Check if same r (nonce reuse attack)
    if len(sigs) >= 2 and sigs[0]['r'] == sigs[1]['r']:
        r = sigs[0]['r']
        s1 = sigs[0]['s']
        s2 = sigs[1]['s']
        z1 = sigs[0]['z']
        z2 = sigs[1]['z']
        
        # k = (z1 - z2) / (s1 - s2) mod n
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        s_diff_inv = modinv(s_diff, n)
        if s_diff_inv is not None:
            k = (z_diff * s_diff_inv) % n
            
            # d = (s * k - z) / r mod n
            r_inv = modinv(r, n)
            if r_inv is not None:
                d = ((s1 * k - z1) * r_inv) % n
                
                # Format as 64 hex characters
                d_hex = format(d, '064x')
                print(json.dumps({"d": d_hex}))
                return
    
    print(json.dumps({"d": "0" * 64}))

if __name__ == "__main__":
    main()