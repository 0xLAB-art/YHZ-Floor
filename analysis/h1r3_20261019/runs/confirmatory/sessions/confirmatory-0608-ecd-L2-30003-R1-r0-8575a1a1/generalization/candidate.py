import json
import sys

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def recover_private_key(r, s1, s2, z1, z2, n):
    """Recover private key from two signatures with same nonce k."""
    # k = (z1 - z2) / (s1 - s2) mod n
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # d = (s*k - z) / r mod n
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

signatures = instance['signatures']

# Find signatures with same r (nonce reuse)
r_map = {}
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find pair with same r
reused_r = None
indices = None
for r, idx_list in r_map.items():
    if len(idx_list) >= 2:
        reused_r = r
        indices = idx_list[:2]
        break

if reused_r is None:
    raise ValueError("No nonce reuse found")

# Extract the two signatures
sig1 = signatures[indices[0]]
sig2 = signatures[indices[1]]

r = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
s2 = int(sig2['s'], 16)
z1 = int(sig1['z'], 16)
z2 = int(sig2['z'], 16)

# Recover private key
d = recover_private_key(r, s1, s2, z1, z2, n)

# Output result
result = {
    "d": format(d, '064x')
}
print(json.dumps(result))
