import json
import sys
import base64

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
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

def decode_base64_int(b64_str):
    """Decode base64 string to integer."""
    data = base64.b64decode(b64_str)
    return int.from_bytes(data, 'big')

# SECP256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Parse signatures
signatures = []
for sig in instance['signatures']:
    r = decode_base64_int(sig['r'])
    s = decode_base64_int(sig['s'])
    z = decode_base64_int(sig['z'])
    signatures.append((r, s, z))

# Find signatures with same r (nonce reuse)
r_to_sigs = {}
for i, (r, s, z) in enumerate(signatures):
    if r not in r_to_sigs:
        r_to_sigs[r] = []
    r_to_sigs[r].append((i, s, z))

# Find a pair with same r
r_shared = None
sig1_data = None
sig2_data = None

for r, sigs in r_to_sigs.items():
    if len(sigs) >= 2:
        r_shared = r
        sig1_data = sigs[0]
        sig2_data = sigs[1]
        break

if r_shared is None:
    raise ValueError("No nonce reuse found")

s1, z1 = sig1_data[1], sig1_data[2]
s2, z2 = sig2_data[1], sig2_data[2]

# Recover k from nonce reuse
# k = (z1 - z2) / (s1 - s2) mod n
z_diff = (z1 - z2) % n
s_diff = (s1 - s2) % n
s_diff_inv = modinv(s_diff, n)
k = (z_diff * s_diff_inv) % n

# Recover private key d
# s1 = k^(-1) * (z1 + r * d) mod n
# s1 * k = z1 + r * d mod n
# d = (s1 * k - z1) / r mod n
r_inv = modinv(r_shared, n)
d = ((s1 * k - z1) * r_inv) % n

# Output as 64 lowercase hex characters
d_hex = format(d, '064x')
print(json.dumps({"d": d_hex}))