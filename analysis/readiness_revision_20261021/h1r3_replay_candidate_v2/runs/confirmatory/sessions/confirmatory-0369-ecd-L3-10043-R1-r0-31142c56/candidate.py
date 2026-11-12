import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = instance['signatures']

# Convert signatures to integers
sigs = []
for sig in signatures:
    sigs.append({
        'r': int(sig['r'], 16),
        's': int(sig['s'], 16),
        'z': int(sig['z'], 16)
    })

# Find signatures with the same r value (indicating same k)
r_map = {}
for i, sig in enumerate(sigs):
    r = sig['r']
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find a pair with the same r
k_found = None
d_found = None

for r_val, indices in r_map.items():
    if len(indices) >= 2:
        # We have at least two signatures with the same r
        i1, i2 = indices[0], indices[1]
        
        r = sigs[i1]['r']
        s1 = sigs[i1]['s']
        s2 = sigs[i2]['s']
        z1 = sigs[i1]['z']
        z2 = sigs[i2]['z']
        
        # Calculate k: k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        
        k = (numerator * modinv(denominator, n)) % n
        
        # Calculate d: d = (s * k - z) / r mod n
        numerator_d = (s1 * k - z1) % n
        d = (numerator_d * modinv(r, n)) % n
        
        k_found = k
        d_found = d
        break

# Format as 64 character lowercase hex
d_hex = format(d_found, '064x')
k_hex = format(k_found, '064x')

result = {
    "d": d_hex,
    "k": k_hex
}

print(json.dumps(result))
