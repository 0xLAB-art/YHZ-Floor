import json
import sys

def modinv(a, m):
    """Modular multiplicative inverse using extended Euclidean algorithm."""
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

def point_on_curve(x, y, p, a, b):
    """Check if point (x, y) is on the curve y^2 = x^3 + ax + b (mod p)."""
    left = (y * y) % p
    right = (x * x * x + a * x + b) % p
    return left == right

# secp256k1 parameters
p_secp256k1 = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n_secp256k1 = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
a_secp256k1 = 0
b_secp256k1 = 7

# secp256r1 (NIST P-256) parameters
p_secp256r1 = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
n_secp256r1 = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
a_secp256r1 = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC
b_secp256r1 = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

x = int(instance['public_key']['x'], 16)
y = int(instance['public_key']['y'], 16)

sig1 = instance['signatures'][0]
sig2 = instance['signatures'][1]

r = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
z1 = int(sig1['z'], 16)

s2 = int(sig2['s'], 16)
z2 = int(sig2['z'], 16)

# Determine which curve
if point_on_curve(x, y, p_secp256k1, a_secp256k1, b_secp256k1):
    n = n_secp256k1
elif point_on_curve(x, y, p_secp256r1, a_secp256r1, b_secp256r1):
    n = n_secp256r1
else:
    raise ValueError("Public key not on known curve")

# Recover private key from nonce reuse
# k = (z1 - z2) * (s1 - s2)^-1 mod n
k = ((z1 - z2) * modinv(s1 - s2, n)) % n

# d = (s1 * k - z1) * r^-1 mod n
d = ((s1 * k - z1) * modinv(r, n)) % n

# Output result
result = {"d": format(d, '064x')}
print(json.dumps(result))
