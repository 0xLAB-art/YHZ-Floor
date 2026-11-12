import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
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

signatures = instance['signatures']

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Find duplicate r values
r_map = {}
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find r values that appear more than once
duplicate_r = None
indices = None
for r, idxs in r_map.items():
    if len(idxs) > 1:
        duplicate_r = r
        indices = idxs[:2]  # Use first two occurrences
        break

if duplicate_r is None:
    raise Exception("No duplicate r values found")

# Get the two signatures with the same r
i1, i2 = indices
sig1 = signatures[i1]
sig2 = signatures[i2]

r = int(sig1['r'], 16)
s1 = int(sig1['s'], 16)
s2 = int(sig2['s'], 16)
z1 = int(sig1['z'], 16)
z2 = int(sig2['z'], 16)

# Recover k from the two signatures
# k = (z1 - z2) / (s1 - s2) mod n
k = ((z1 - z2) % n * modinv((s1 - s2) % n, n)) % n

# Recover private key d
# d = (s*k - z) / r mod n
d = ((s1 * k - z1) % n * modinv(r, n)) % n

# Format as 64 lowercase hex characters
k_hex = format(k, '064x')
d_hex = format(d, '064x')

result = {
    "d": d_hex,
    "k": k_hex
}

print(json.dumps(result))
