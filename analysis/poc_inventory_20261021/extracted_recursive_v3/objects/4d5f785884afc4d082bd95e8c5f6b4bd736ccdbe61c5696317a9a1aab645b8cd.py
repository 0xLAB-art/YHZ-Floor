import sys
import json
import base64
import hashlib

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Decode public key
pub_x = int.from_bytes(base64.b64decode(instance['public_key']['x']), 'big')
pub_y = int.from_bytes(base64.b64decode(instance['public_key']['y']), 'big')

# Decode signatures
signatures = []
for sig in instance['signatures']:
    r = int.from_bytes(base64.b64decode(sig['r']), 'big')
    s = int.from_bytes(base64.b64decode(sig['s']), 'big')
    z = int.from_bytes(base64.b64decode(sig['z']), 'big')
    signatures.append((r, s, z))

# Look for duplicate r values (nonce reuse attack)
r_map = {}
for i, (r, s, z) in enumerate(signatures):
    if r in r_map:
        # Found duplicate r! Extract private key
        j = r_map[r]
        r1, s1, z1 = signatures[j]
        r2, s2, z2 = signatures[i]
        
        # k = (z1 - z2) / (s1 - s2) mod n
        # d = (s*k - z) / r mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        s_diff_inv = modinv(s_diff, n)
        if s_diff_inv is None:
            continue
            
        k = (z_diff * s_diff_inv) % n
        
        # Calculate private key d from first signature
        r_inv = modinv(r1, n)
        if r_inv is None:
            continue
            
        d = (r_inv * (s1 * k - z1)) % n
        
        # Verify with second signature
        d2 = (r_inv * (s2 * k - z2)) % n
        
        if d == d2 and d > 0:
            # Convert to hex
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            
            print(json.dumps(result))
            sys.exit(0)
    else:
        r_map[r] = i

# Should not reach here if there's a nonce reuse
print(json.dumps({"d": "0" * 64, "k": "0" * 64}))