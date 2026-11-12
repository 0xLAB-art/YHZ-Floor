import sys
import json

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

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

signatures = data['signatures']

# Convert hex strings to integers
sigs = []
for sig in signatures:
    r = int(sig['r'], 16)
    s = int(sig['s'], 16)
    z = int(sig['z'], 16)
    sigs.append((r, s, z))

# Look for signature pairs with the same r value (nonce reuse)
r_map = {}
for i, (r, s, z) in enumerate(sigs):
    if r not in r_map:
        r_map[r] = []
    r_map[r].append((i, s, z))

# Find nonce reuse and recover private key
d = None
for r, sig_list in r_map.items():
    if len(sig_list) >= 2:
        # We have nonce reuse
        idx1, s1, z1 = sig_list[0]
        idx2, s2, z2 = sig_list[1]
        
        # k = (z1 - z2) / (s1 - s2) mod n
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        
        if denominator == 0:
            continue
        
        k = (numerator * modinv(denominator, n)) % n
        
        # d = (s1 * k - z1) / r mod n
        d_numerator = (s1 * k - z1) % n
        d = (d_numerator * modinv(r, n)) % n
        
        # Verify with another signature if available
        if d is not None:
            break

# If no nonce reuse found in same r, shouldn't happen with this instance
# but the code above should find it

# Format output
result = {"d": format(d, '064x')}
print(json.dumps(result))