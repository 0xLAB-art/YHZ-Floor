import json
import sys
from collections import defaultdict

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

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

signatures = instance['signatures']

# Group signatures by r value
r_groups = defaultdict(list)
for sig in signatures:
    r = int(sig['r'], 16)
    s = int(sig['s'], 16)
    z = int(sig['z'], 16)
    r_groups[r].append((s, z))

# Find r values that appear more than once
d = None
k = None

for r, sig_list in r_groups.items():
    if len(sig_list) >= 2:
        # Use first two signatures with same r
        s1, z1 = sig_list[0]
        s2, z2 = sig_list[1]
        
        # Calculate k: k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        
        if denominator == 0:
            continue
        
        k_calc = (numerator * modinv(denominator, n)) % n
        
        # Calculate d: d = (s*k - z) / r mod n
        d_calc = ((s1 * k_calc - z1) % n * modinv(r, n)) % n
        
        # Verify with second signature
        d_verify = ((s2 * k_calc - z2) % n * modinv(r, n)) % n
        
        if d_calc == d_verify:
            d = d_calc
            k = k_calc
            break

# Format output
result = {
    "d": format(d, '064x'),
    "k": format(k, '064x')
}

print(json.dumps(result))
