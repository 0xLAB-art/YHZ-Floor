import sys
import json
import base64
from typing import List, Tuple


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    gcd_val, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd_val, x, y

def mod_inverse(a: int, m: int) -> int:
    gcd_val, x, _ = extended_gcd(a, m)
    if gcd_val != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def bytes_to_int(b: bytes) -> int:
    return int.from_bytes(b, 'big')

def int_to_hex(n: int) -> str:
    return hex(n)[2:].zfill(64)

# ECDSA parameters for secp256k1
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# Decode public key
pub_x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
pub_y = bytes_to_int(base64.b64decode(instance['public_key']['y']))

# Decode signatures
signatures = []
for sig in instance['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append((r, s, z))

# Look for duplicate r values (nonce reuse attack)
r_map = {}
for i, (r, s, z) in enumerate(signatures):
    if r in r_map:
        r_map[r].append((i, s, z))
    else:
        r_map[r] = [(i, s, z)]

# Find pairs with same r
for r, sigs in r_map.items():
    if len(sigs) >= 2:
        # We have nonce reuse!
        i1, s1, z1 = sigs[0]
        i2, s2, z2 = sigs[1]
        
        # k = (z1 - z2) / (s1 - s2) mod n
        # d = (s*k - z) / r mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        if s_diff == 0:
            continue
            
        s_diff_inv = mod_inverse(s_diff, n)
        k = (z_diff * s_diff_inv) % n
        
        # Now recover private key d
        r_inv = mod_inverse(r, n)
        d = ((s1 * k - z1) * r_inv) % n
        
        # Output the private key
        result = {"d": int_to_hex(d)}
        print(json.dumps(result))
        sys.exit(0)

# If no nonce reuse found, try other attacks
# This shouldn't happen based on the instance, but just in case
result = {"d": "0" * 64}
print(json.dumps(result))
