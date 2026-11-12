import json
import sys
import base64
import hashlib

def base64_to_int(b64_str):
    """Convert base64 string to integer."""
    decoded = base64.b64decode(b64_str)
    return int.from_bytes(decoded, 'big')

def int_to_hex(n):
    """Convert integer to 64-character lowercase hex string."""
    hex_str = hex(n)[2:]  # Remove '0x' prefix
    return hex_str.zfill(64)

def modinv(a, m):
    """Compute modular inverse of a modulo m."""
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
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key and signatures
    signatures = []
    for sig in instance['signatures']:
        r = base64_to_int(sig['r'])
        s = base64_to_int(sig['s'])
        z = base64_to_int(sig['z'])
        signatures.append({'r': r, 's': s, 'z': z})
    
    # SECP256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with the same r value (nonce reuse)
    r_to_indices = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_to_indices:
            r_to_indices[r] = []
        r_to_indices[r].append(i)
    
    # Find a pair with reused nonce
    d = None
    k = None
    
    for r, indices in r_to_indices.items():
        if len(indices) >= 2:
            # Use first two signatures with same r
            i1, i2 = indices[0], indices[1]
            sig1 = signatures[i1]
            sig2 = signatures[i2]
            
            r = sig1['r']
            s1 = sig1['s']
            s2 = sig2['s']
            z1 = sig1['z']
            z2 = sig2['z']
            
            # Calculate k = (z1 - z2) / (s1 - s2) mod n
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Calculate d = (s*k - z) / r mod n
            r_inv = modinv(r, n)
            d = ((s1 * k - z1) * r_inv) % n
            
            break
    
    # Output result
    result = {
        "d": int_to_hex(d),
        "k": int_to_hex(k)
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()