import sys
import json
import base64


def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# Decode public key
pub_x = bytes_to_int(base64.b64decode(data['public_key']['x']))
pub_y = bytes_to_int(base64.b64decode(data['public_key']['y']))

# Decode signatures
signatures = []
for sig in data['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append((r, s, z))

# Find duplicate r values (nonce reuse)
r_map = {}
for i, (r, s, z) in enumerate(signatures):
    if r not in r_map:
        r_map[r] = []
    r_map[r].append((i, s, z))

# Find a pair with the same r
reused_r = None
sig1_data = None
sig2_data = None

for r, sigs in r_map.items():
    if len(sigs) >= 2:
        reused_r = r
        sig1_data = sigs[0]  # (index, s1, z1)
        sig2_data = sigs[1]  # (index, s2, z2)
        break

if reused_r is None:
    raise Exception("No nonce reuse found")

_, s1, z1 = sig1_data
_, s2, z2 = sig2_data
r = reused_r

# Recover k from nonce reuse
# s1 - s2 = k^(-1) * (z1 - z2) mod n
# k = (z1 - z2) / (s1 - s2) mod n

s_diff = (s1 - s2) % n
z_diff = (z1 - z2) % n

k = (z_diff * modinv(s_diff, n)) % n

# Recover private key d
# s1 = k^(-1) * (z1 + r*d) mod n
# s1 * k = z1 + r*d mod n
# d = (s1*k - z1) / r mod n

d = ((s1 * k - z1) % n * modinv(r, n)) % n

# Output result
result = {
    "d": int_to_hex(d),
    "k": int_to_hex(k)
}

print(json.dumps(result))
