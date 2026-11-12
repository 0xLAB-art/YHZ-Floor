import json
import sys

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

signatures = data['signatures']

# secp256k1 parameters
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Find duplicate r values
r_map = {}
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with same r
d = None
k = None

for r_val, indices in r_map.items():
    if len(indices) >= 2:
        # Use first two signatures with same r
        i1, i2 = indices[0], indices[1]
        
        r = int(signatures[i1]['r'], 16)
        s1 = int(signatures[i1]['s'], 16)
        z1 = int(signatures[i1]['z'], 16)
        s2 = int(signatures[i2]['s'], 16)
        z2 = int(signatures[i2]['z'], 16)
        
        # Recover k: k = (z1 - z2) / (s1 - s2) mod n
        k = ((z1 - z2) * modinv(s1 - s2, n)) % n
        
        # Recover d: d = (s1 * k - z1) / r mod n
        d = ((s1 * k - z1) * modinv(r, n)) % n
        
        break

# Format output
d_hex = format(d, '064x')
k_hex = format(k, '064x')

result = {
    "d": d_hex,
    "k": k_hex
}

print(json.dumps(result))