import json
import sys
import base64


def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

# SECP256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# Decode signatures
signatures = []
for sig in data['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append((r, s, z))

# Find duplicate r values
r_groups = {}
for i, (r, s, z) in enumerate(signatures):
    if r not in r_groups:
        r_groups[r] = []
    r_groups[r].append((i, s, z))

# Find a pair with duplicate r
k_found = None
d_found = None

for r, sigs in r_groups.items():
    if len(sigs) >= 2:
        # Use first two signatures with same r
        i1, s1, z1 = sigs[0]
        i2, s2, z2 = sigs[1]
        
        # Calculate k = (z1 - z2) / (s1 - s2) mod n
        z_diff = (z1 - z2) % n
        s_diff = (s1 - s2) % n
        
        if s_diff == 0:
            continue
            
        s_diff_inv = modinv(s_diff, n)
        k = (z_diff * s_diff_inv) % n
        
        # Calculate d = (s * k - z) / r mod n
        r_inv = modinv(r, n)
        d = ((s1 * k - z1) * r_inv) % n
        
        k_found = k
        d_found = d
        break

# Output result
result = {
    "d": int_to_hex(d_found),
    "k": int_to_hex(k_found)
}
print(json.dumps(result))
