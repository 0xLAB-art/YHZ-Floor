import sys
import json
import base64


def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

def mod_inverse(a, m):
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

# Decode signatures
signatures = []
for sig in instance['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append((r, s, z))

# NIST P-256 curve order
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

# Find duplicate r values
r_dict = {}
for i, (r, s, z) in enumerate(signatures):
    if r in r_dict:
        r_dict[r].append((i, s, z))
    else:
        r_dict[r] = [(i, s, z)]

# Find a pair with duplicate r
d = None
k = None

for r, sig_list in r_dict.items():
    if len(sig_list) >= 2:
        # Use first two signatures with same r
        i1, s1, z1 = sig_list[0]
        i2, s2, z2 = sig_list[1]
        
        # Calculate k from the pair
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        if s_diff == 0:
            continue
            
        s_diff_inv = mod_inverse(s_diff, n)
        k_candidate = (z_diff * s_diff_inv) % n
        
        # Calculate d from k
        r_inv = mod_inverse(r, n)
        d_candidate = ((s1 * k_candidate - z1) * r_inv) % n
        
        # Verify with the second signature
        d_candidate2 = ((s2 * k_candidate - z2) * r_inv) % n
        
        if d_candidate == d_candidate2:
            d = d_candidate
            k = k_candidate
            break

# Output result
result = {
    "d": int_to_hex(d),
    "k": int_to_hex(k)
}

print(json.dumps(result))
