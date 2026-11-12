import sys
import json
from collections import defaultdict

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

public_key = data['public_key']
signatures = data['signatures']

# Group signatures by r value
r_groups = defaultdict(list)
for sig in signatures:
    r = int(sig['r'], 16)
    s = int(sig['s'], 16)
    z = int(sig['z'], 16)
    r_groups[r].append((s, z))

# Find duplicate r values and try to extract k and d
k_found = None
d_found = None

for r, sig_list in r_groups.items():
    if len(sig_list) >= 2:
        # We have at least two signatures with the same r (same k)
        s1, z1 = sig_list[0]
        s2, z2 = sig_list[1]
        
        # From ECDSA: s = (z + r*d) / k mod n
        # s1*k = z1 + r*d mod n
        # s2*k = z2 + r*d mod n
        # s1*k - s2*k = z1 - z2 mod n
        # k(s1 - s2) = z1 - z2 mod n
        # k = (z1 - z2) / (s1 - s2) mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        s_diff_inv = modinv(s_diff, n)
        if s_diff_inv is not None:
            k = (z_diff * s_diff_inv) % n
            
            # Now recover d from: s = (z + r*d) / k mod n
            # s*k = z + r*d mod n
            # r*d = s*k - z mod n
            # d = (s*k - z) / r mod n
            
            r_inv = modinv(r, n)
            if r_inv is not None:
                d = ((s1 * k - z1) * r_inv) % n
                
                # Verify with second signature
                d_check = ((s2 * k - z2) * r_inv) % n
                
                if d == d_check and d > 0:
                    k_found = k
                    d_found = d
                    break

# Format output
if k_found is not None and d_found is not None:
    k_hex = format(k_found, '064x')
    d_hex = format(d_found, '064x')
else:
    k_hex = '0' * 64
    d_hex = '0' * 64

result = {
    "d": d_hex,
    "k": k_hex
}

print(json.dumps(result))
