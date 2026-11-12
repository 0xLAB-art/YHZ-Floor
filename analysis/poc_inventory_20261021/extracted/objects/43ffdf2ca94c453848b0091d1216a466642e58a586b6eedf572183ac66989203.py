import json
import sys
import hashlib
from collections import defaultdict

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def bytes_to_int(b):
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    """Convert integer to 64-character hex string."""
    return format(n, '064x')

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.loads(f.read())
    
    # Decode base64 values
    import base64
    
    public_key = data['public_key']
    px = bytes_to_int(base64.b64decode(public_key['x']))
    py = bytes_to_int(base64.b64decode(public_key['y']))
    
    signatures = []
    for sig in data['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Group signatures by r value to find nonce reuse
    r_groups = defaultdict(list)
    for i, (r, s, z) in enumerate(signatures):
        r_groups[r].append((i, s, z))
    
    # Look for duplicate r values (nonce reuse)
    d = None
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Nonce reuse detected
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            # Calculate private key using nonce reuse attack
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s1 * k - z1) / r mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
            
            # k = z_diff / s_diff mod n
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # d = (s1 * k - z1) / r mod n
            r_inv = modinv(r, n)
            d = ((s1 * k - z1) * r_inv) % n
            
            # Verify with another signature if available
            break
    
    if d is None:
        # Fallback: try all pairs
        for i in range(len(signatures)):
            for j in range(i + 1, len(signatures)):
                r1, s1, z1 = signatures[i]
                r2, s2, z2 = signatures[j]
                
                if r1 == r2:
                    s_diff = (s1 - s2) % n
                    z_diff = (z1 - z2) % n
                    
                    if s_diff == 0:
                        continue
                    
                    s_diff_inv = modinv(s_diff, n)
                    k = (z_diff * s_diff_inv) % n
                    
                    r_inv = modinv(r1, n)
                    d = ((s1 * k - z1) * r_inv) % n
                    break
            if d is not None:
                break
    
    # Output result
    result = {"d": int_to_hex(d)}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
