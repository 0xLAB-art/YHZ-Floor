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

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Decode public key
x = int.from_bytes(base64.b64decode(instance['public_key']['x']), 'big')
y = int.from_bytes(base64.b64decode(instance['public_key']['y']), 'big')

# Decode signatures
signatures = []
for sig in instance['signatures']:
    r = int.from_bytes(base64.b64decode(sig['r']), 'big')
    s = int.from_bytes(base64.b64decode(sig['s']), 'big')
    z = int.from_bytes(base64.b64decode(sig['z']), 'big')
    signatures.append((r, s, z))

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Find duplicate r values (nonce reuse)
r_map = {}
for i, (r, s, z) in enumerate(signatures):
    if r not in r_map:
        r_map[r] = []
    r_map[r].append((i, s, z))

# Look for nonce reuse attack
d = None
for r, sigs in r_map.items():
    if len(sigs) >= 2:
        # We have nonce reuse with same r
        i1, s1, z1 = sigs[0]
        i2, s2, z2 = sigs[1]
        
        # k = (z1 - z2) / (s1 - s2) mod n
        # d = (s * k - z) / r mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        if s_diff != 0:
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Now recover d from first signature
            # s1 = k^-1 * (z1 + r * d) mod n
            # s1 * k = z1 + r * d mod n
            # d = (s1 * k - z1) / r mod n
            
            d = ((s1 * k - z1) * modinv(r, n)) % n
            break

if d is None:
    # If no nonce reuse, output zero (shouldn't happen in this challenge)
    d = 0

# Format as 64 lowercase hex characters
d_hex = format(d, '064x')

# Output
print(json.dumps({"d": d_hex}))
