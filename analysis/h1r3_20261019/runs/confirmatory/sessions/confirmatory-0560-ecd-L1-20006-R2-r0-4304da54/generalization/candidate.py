import json
import sys
import base64

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
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

def decode_base64_to_int(b64_str):
    """Decode base64 string to integer"""
    decoded = base64.b64decode(b64_str)
    return int.from_bytes(decoded, 'big')

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Parse signatures
sig1 = instance['signatures'][0]
sig2 = instance['signatures'][1]

r = decode_base64_to_int(sig1['r'])
s1 = decode_base64_to_int(sig1['s'])
z1 = decode_base64_to_int(sig1['z'])

s2 = decode_base64_to_int(sig2['s'])
z2 = decode_base64_to_int(sig2['z'])

# Recover k from the two signatures with same r
z_diff = (z1 - z2) % n
s_diff = (s1 - s2) % n
s_diff_inv = modinv(s_diff, n)
k = (z_diff * s_diff_inv) % n

# Recover private key d
k_inv = modinv(k, n)
d = ((s1 * k - z1) * modinv(r, n)) % n

# Output result
result = {
    "d": format(d, '064x')
}
print(json.dumps(result))
