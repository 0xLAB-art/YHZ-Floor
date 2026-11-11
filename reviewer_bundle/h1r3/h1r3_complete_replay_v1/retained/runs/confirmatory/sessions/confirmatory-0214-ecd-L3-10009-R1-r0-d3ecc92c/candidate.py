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
    instance = json.load(f)

signatures = instance['signatures']

# Look for repeated r values (nonce reuse)
r_dict = {}
for i, sig in enumerate(signatures):
    r = int(sig['r'], 16)
    if r in r_dict:
        r_dict[r].append(i)
    else:
        r_dict[r] = [i]

# Find nonce reuse
k_found = None
d_found = None

for r, indices in r_dict.items():
    if len(indices) >= 2:
        # We have nonce reuse!
        i1, i2 = indices[0], indices[1]
        
        r1 = int(signatures[i1]['r'], 16)
        s1 = int(signatures[i1]['s'], 16)
        z1 = int(signatures[i1]['z'], 16)
        
        r2 = int(signatures[i2]['r'], 16)
        s2 = int(signatures[i2]['s'], 16)
        z2 = int(signatures[i2]['z'], 16)
        
        # From ECDSA: s = k^(-1) * (z + r*d) mod n
        # s1 = k^(-1) * (z1 + r*d) mod n
        # s2 = k^(-1) * (z2 + r*d) mod n
        # s1 - s2 = k^(-1) * (z1 - z2) mod n
        # k = (z1 - z2) / (s1 - s2) mod n
        
        s_diff = (s1 - s2) % n
        z_diff = (z1 - z2) % n
        
        if s_diff != 0:
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Now recover private key d
            # s1 = k^(-1) * (z1 + r*d) mod n
            # s1 * k = z1 + r*d mod n
            # d = (s1 * k - z1) / r mod n
            
            k_inv = modinv(k, n)
            d = ((s1 * k - z1) * modinv(r1, n)) % n
            
            # Verify with second signature
            d_verify = ((s2 * k - z2) * modinv(r2, n)) % n
            
            if d == d_verify and d != 0 and k != 0:
                k_found = k
                d_found = d
                break

# Format output
if k_found is not None and d_found is not None:
    k_hex = format(k_found, '064x')
    d_hex = format(d_found, '064x')
else:
    # Fallback (shouldn't happen with valid input)
    k_hex = '0' * 64
    d_hex = '0' * 64

result = {
    "d": d_hex,
    "k": k_hex
}

print(json.dumps(result))
