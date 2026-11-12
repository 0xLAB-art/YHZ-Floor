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
    """Convert integer to 64-character lowercase hex string."""
    return format(n, '064x')

# ECDSA parameters for secp256k1
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Decode public key
pub_x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
pub_y = bytes_to_int(base64.b64decode(instance['public_key']['y']))

# Decode signatures
signatures = []
for sig in instance['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append((r, s, z))

# Look for duplicate r values (nonce reuse)
r_dict = {}
for i, (r, s, z) in enumerate(signatures):
    if r in r_dict:
        r_dict[r].append((s, z, i))
    else:
        r_dict[r] = [(s, z, i)]

# Find k and d from nonce reuse
k_found = None
d_found = None

for r, sig_list in r_dict.items():
    if len(sig_list) >= 2:
        # We have nonce reuse
        s1, z1, _ = sig_list[0]
        s2, z2, _ = sig_list[1]
        
        # k = (z1 - z2) / (s1 - s2) mod n
        # d = (s*k - z) / r mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        try:
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Verify and compute d
            r_inv = modinv(r, n)
            d = (r_inv * (s1 * k - z1)) % n
            
            # Verify with second signature
            d_check = (r_inv * (s2 * k - z2)) % n
            
            if d == d_check:
                k_found = k
                d_found = d
                break
        except:
            continue

# Output result
result = {
    "d": int_to_hex(d_found),
    "k": int_to_hex(k_found)
}

print(json.dumps(result))