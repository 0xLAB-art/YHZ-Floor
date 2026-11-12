import json
import sys
import base64

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

def modinv(a, m):
    """Modular multiplicative inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
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
    instance = json.load(f)

# SECP256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Parse signatures
signatures = []
for sig in instance['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append((r, s, z))

# Find duplicate r values
r_map = {}
for i, (r, s, z) in enumerate(signatures):
    if r in r_map:
        # Found duplicate r - we can recover k and d
        j = r_map[r]
        r1, s1, z1 = signatures[j]
        r2, s2, z2 = signatures[i]
        
        # Calculate k = (z1 - z2) / (s1 - s2) mod n
        k = ((z1 - z2) * modinv(s1 - s2, n)) % n
        
        # Calculate d = (s*k - z) / r mod n
        d = ((s1 * k - z1) * modinv(r1, n)) % n
        
        # Output result
        result = {
            "d": int_to_hex(d),
            "k": int_to_hex(k)
        }
        print(json.dumps(result))
        sys.exit(0)
    else:
        r_map[r] = i
