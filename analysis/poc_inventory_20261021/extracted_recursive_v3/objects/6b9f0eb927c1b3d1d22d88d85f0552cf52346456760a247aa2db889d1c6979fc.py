import sys
import json
import base64
from typing import Tuple
from collections import defaultdict

def mod_inverse(a: int, m: int) -> int:
    """Compute modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def bytes_to_int(b: bytes) -> int:
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n: int) -> str:
    """Convert integer to 64-character hex string."""
    return format(n, '064x')

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

# Standard secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Look for nonce reuse - same r value means same k
r_map = defaultdict(list)
for i, (r, s, z) in enumerate(signatures):
    r_map[r].append((i, s, z))

# Find private key from nonce reuse
d = None
k = None

for r, sig_list in r_map.items():
    if len(sig_list) >= 2:
        # We have nonce reuse!
        idx1, s1, z1 = sig_list[0]
        idx2, s2, z2 = sig_list[1]
        
        # From ECDSA: s = k^(-1) * (z + r*d) mod n
        # s1 = k^(-1) * (z1 + r*d) mod n
        # s2 = k^(-1) * (z2 + r*d) mod n
        # s1 - s2 = k^(-1) * (z1 - z2) mod n
        # k = (z1 - z2) / (s1 - s2) mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        if s_diff == 0:
            continue
        
        s_diff_inv = mod_inverse(s_diff, n)
        k_candidate = (z_diff * s_diff_inv) % n
        
        # Recover d from: s1 = k^(-1) * (z1 + r*d) mod n
        # k * s1 = z1 + r*d mod n
        # d = (k * s1 - z1) / r mod n
        
        if r == 0:
            continue
        
        r_inv = mod_inverse(r, n)
        d_candidate = ((k_candidate * s1 - z1) * r_inv) % n
        
        # Verify with another signature
        for idx, s, z in sig_list[:3]:
            # Check: s * k = z + r * d (mod n)
            left = (s * k_candidate) % n
            right = (z + r * d_candidate) % n
            if left == right:
                d = d_candidate
                k = k_candidate
                break
        
        if d is not None:
            break

# Output result
result = {
    "d": int_to_hex(d),
    "k": int_to_hex(k)
}

print(json.dumps(result))