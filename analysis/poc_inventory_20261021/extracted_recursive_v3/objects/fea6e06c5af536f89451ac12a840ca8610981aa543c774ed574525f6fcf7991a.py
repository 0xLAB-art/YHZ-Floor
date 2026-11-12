import json
import sys
import base64
from typing import Tuple

def mod_inverse(a: int, m: int) -> int:
    """Compute modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def decode_base64_to_int(b64_str: str) -> int:
    """Decode base64 string to integer."""
    decoded = base64.b64decode(b64_str)
    return int.from_bytes(decoded, byteorder='big')

# NIST P-256 curve parameters
p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

# Read input
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# Decode public key
x = decode_base64_to_int(data['public_key']['x'])
y = decode_base64_to_int(data['public_key']['y'])

# Decode signatures
sig1 = data['signatures'][0]
r1 = decode_base64_to_int(sig1['r'])
s1 = decode_base64_to_int(sig1['s'])
z1 = decode_base64_to_int(sig1['z'])

sig2 = data['signatures'][1]
r2 = decode_base64_to_int(sig2['r'])
s2 = decode_base64_to_int(sig2['s'])
z2 = decode_base64_to_int(sig2['z'])

# Both signatures share the same r value (nonce reuse vulnerability)
# ECDSA equations:
# s1 = (z1 + r1*d) / k mod n
# s2 = (z2 + r2*d) / k mod n
# Since r1 == r2, we can solve for k and then d

# From the equations:
# k = (z1 - z2) / (s1 - s2) mod n
s_diff = (s1 - s2) % n
z_diff = (z1 - z2) % n
s_diff_inv = mod_inverse(s_diff, n)
k = (z_diff * s_diff_inv) % n

# Now recover private key d:
# d = (s1*k - z1) / r1 mod n
r1_inv = mod_inverse(r1, n)
d = ((s1 * k - z1) * r1_inv) % n

# Output the private key as 64 lowercase hex characters
d_hex = format(d, '064x')
print(json.dumps({"d": d_hex}))