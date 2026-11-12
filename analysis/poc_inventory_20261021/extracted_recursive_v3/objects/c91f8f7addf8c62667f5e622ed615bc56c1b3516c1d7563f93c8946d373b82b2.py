import json
import sys
import base64
from hashlib import sha256

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

# Parse public key
pub_x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
pub_y = bytes_to_int(base64.b64decode(instance['public_key']['y']))

# Parse signatures
signatures = []
for sig in instance['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append((r, s, z))

# Look for repeated r values (nonce reuse)
r_map = {}
for i, (r, s, z) in enumerate(signatures):
    if r not in r_map:
        r_map[r] = []
    r_map[r].append((i, s, z))

# Find nonce reuse and recover private key
d = None
k = None

for r, sigs in r_map.items():
    if len(sigs) >= 2:
        # We have nonce reuse
        i1, s1, z1 = sigs[0]
        i2, s2, z2 = sigs[1]
        
        # k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        
        if denominator != 0:
            k_recovered = (numerator * modinv(denominator, n)) % n
            
            # Verify and compute d = (s*k - z) / r mod n
            r_inv = modinv(r, n)
            d_recovered = ((s1 * k_recovered - z1) * r_inv) % n
            
            # Store results
            d = d_recovered
            k = k_recovered
            break

# Output result
result = {
    "d": int_to_hex(d),
    "k": int_to_hex(k)
}
print(json.dumps(result))