import json
import sys
import base64

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

def modinv(a, m):
    # Extended Euclidean algorithm for modular inverse
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
    data = json.load(f)

# SECP256K1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Parse public key
pub_x = bytes_to_int(base64.b64decode(data['public_key']['x']))
pub_y = bytes_to_int(base64.b64decode(data['public_key']['y']))

# Parse signatures
signatures = []
for sig in data['signatures']:
    r = bytes_to_int(base64.b64decode(sig['r']))
    s = bytes_to_int(base64.b64decode(sig['s']))
    z = bytes_to_int(base64.b64decode(sig['z']))
    signatures.append((r, s, z))

# Find duplicate r values (nonce reuse)
r_map = {}
for i, (r, s, z) in enumerate(signatures):
    if r not in r_map:
        r_map[r] = []
    r_map[r].append((i, s, z))

# Look for reused nonces
for r, occurrences in r_map.items():
    if len(occurrences) >= 2:
        # We have nonce reuse!
        i1, s1, z1 = occurrences[0]
        i2, s2, z2 = occurrences[1]
        
        # From s1 = k^(-1) * (z1 + r*d) mod n
        # and s2 = k^(-1) * (z2 + r*d) mod n
        # We get: s1 - s2 = k^(-1) * (z1 - z2) mod n
        # So: k = (z1 - z2) / (s1 - s2) mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        if s_diff != 0:
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Now recover d from: s1 = k^(-1) * (z1 + r*d) mod n
            # So: s1 * k = z1 + r*d mod n
            # Thus: d = (s1 * k - z1) / r mod n
            
            k_inv = modinv(k, n)
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            # Output result
            result = {
                "d": int_to_hex(d),
                "k": int_to_hex(k)
            }
            print(json.dumps(result))
            sys.exit(0)

# Should not reach here if nonce reuse exists
print(json.dumps({"d": "0" * 64, "k": "0" * 64}))
