import sys
import json
import base64

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

# Look for repeated r values (nonce reuse attack)
r_dict = {}
for i, (r, s, z) in enumerate(signatures):
    if r not in r_dict:
        r_dict[r] = []
    r_dict[r].append((i, s, z))

# Find k and d from nonce reuse
k = None
d = None

for r, sig_list in r_dict.items():
    if len(sig_list) >= 2:
        # We have at least two signatures with the same r (same k)
        i1, s1, z1 = sig_list[0]
        i2, s2, z2 = sig_list[1]
        
        # From ECDSA: s = k^(-1) * (z + r*d) mod n
        # s1 = k^(-1) * (z1 + r*d) mod n
        # s2 = k^(-1) * (z2 + r*d) mod n
        # s1 - s2 = k^(-1) * (z1 - z2) mod n
        # k = (z1 - z2) / (s1 - s2) mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        s_diff_inv = modinv(s_diff, n)
        if s_diff_inv is not None:
            k = (z_diff * s_diff_inv) % n
            
            # Now recover d from: s1 = k^(-1) * (z1 + r*d) mod n
            # s1 * k = z1 + r*d mod n
            # d = (s1 * k - z1) / r mod n
            
            k_inv = modinv(k, n)
            if k_inv is not None:
                r_inv = modinv(r, n)
                if r_inv is not None:
                    d = ((s1 * k - z1) * r_inv) % n
                    break

# Output result
result = {
    "d": int_to_hex(d),
    "k": int_to_hex(k)
}
print(json.dumps(result))
