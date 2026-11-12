import json
import sys
import base64

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Parse signatures
signatures = []
for sig in instance['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append((r, s, z))

# Find signatures with same r (nonce reuse)
r_map = {}
for i, (r, s, z) in enumerate(signatures):
    if r not in r_map:
        r_map[r] = []
    r_map[r].append((i, s, z))

# Find a pair with reused nonce
reused_r = None
sig1_data = None
sig2_data = None

for r, sigs in r_map.items():
    if len(sigs) >= 2:
        reused_r = r
        sig1_data = sigs[0]
        sig2_data = sigs[1]
        break

# Extract values
r = reused_r
s1, z1 = sig1_data[1], sig1_data[2]
s2, z2 = sig2_data[1], sig2_data[2]

# Recover k: k = (z1 - z2) / (s1 - s2) mod n
numerator = (z1 - z2) % n
denominator = (s1 - s2) % n
k = (numerator * modinv(denominator, n)) % n

# Recover d: d = (s * k - z) / r mod n
numerator = (s1 * k - z1) % n
denominator = r
d = (numerator * modinv(denominator, n)) % n

# Output
result = {
    "d": int_to_hex(d),
    "k": int_to_hex(k)
}

print(json.dumps(result))