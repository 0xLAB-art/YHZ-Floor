import json
import sys

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# ECDSA parameters for secp256k1
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Parse public key
Qx = int(instance['public_key']['x'], 16)
Qy = int(instance['public_key']['y'], 16)

# Parse signatures
signatures = []
for sig in instance['signatures']:
    r = int(sig['r'], 16)
    s = int(sig['s'], 16)
    z = int(sig['z'], 16)
    signatures.append((r, s, z))

# Look for nonce reuse (same r value in different signatures)
r_groups = {}
for i, (r, s, z) in enumerate(signatures):
    if r not in r_groups:
        r_groups[r] = []
    r_groups[r].append((i, s, z))

# Find pairs with same r
for r, sigs in r_groups.items():
    if len(sigs) >= 2:
        # We have nonce reuse! Extract private key
        i1, s1, z1 = sigs[0]
        i2, s2, z2 = sigs[1]
        
        # k = (z1 - z2) / (s1 - s2) mod n
        # d = (s1 * k - z1) / r mod n
        
        numerator = (z1 - z2) % n
        denominator = (s1 - s2) % n
        
        denom_inv = modinv(denominator, n)
        if denom_inv is None:
            continue
            
        k = (numerator * denom_inv) % n
        
        # Now recover private key d
        r_inv = modinv(r, n)
        if r_inv is None:
            continue
            
        d = (r_inv * ((s1 * k - z1) % n)) % n
        
        # Verify with all signatures
        valid = True
        for r_sig, s_sig, z_sig in signatures:
            # Verify: k = (z + rd)/s mod n for some k
            # Or equivalently: s*k = z + r*d mod n
            k_test = (modinv(s_sig, n) * (z_sig + r_sig * d)) % n
            if k_test is None:
                valid = False
                break
        
        if valid:
            result = {
                "status": "UNDERDETERMINED",
                "reason": f"private key recovered via nonce reuse: {hex(d)}"
            }
            print(json.dumps(result))
            sys.exit(0)

# No nonce reuse found
result = {
    "status": "UNDERDETERMINED",
    "reason": "no obvious vulnerability detected in signatures"
}
print(json.dumps(result))