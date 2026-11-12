import json
import sys
import base64

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = egcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = egcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def bytes_to_int(b):
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    """Convert integer to 64-character lowercase hex string."""
    return format(n, '064x')

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Parse signatures
signatures = []
for sig in instance['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append({'r': r, 's': s, 'z': z})

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Find duplicate r values
r_map = {}
for i, sig in enumerate(signatures):
    r = sig['r']
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with duplicate r
d = None
k = None

for r, indices in r_map.items():
    if len(indices) >= 2:
        # Use first two signatures with same r
        i1, i2 = indices[0], indices[1]
        sig1 = signatures[i1]
        sig2 = signatures[i2]
        
        r = sig1['r']
        s1 = sig1['s']
        z1 = sig1['z']
        s2 = sig2['s']
        z2 = sig2['z']
        
        # Recover k: k = (z1 - z2) * (s1 - s2)^(-1) mod n
        z_diff = (z1 - z2) % n
        s_diff = (s1 - s2) % n
        s_diff_inv = modinv(s_diff, n)
        k = (z_diff * s_diff_inv) % n
        
        # Recover d: d = (s*k - z) * r^(-1) mod n
        r_inv = modinv(r, n)
        d = ((s1 * k - z1) * r_inv) % n
        
        break

# Output result
result = {
    'd': int_to_hex(d),
    'k': int_to_hex(k)
}

print(json.dumps(result))
