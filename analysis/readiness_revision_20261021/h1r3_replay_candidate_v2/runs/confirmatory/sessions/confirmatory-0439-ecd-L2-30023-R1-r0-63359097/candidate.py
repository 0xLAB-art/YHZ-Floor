import json
import sys

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def recover_private_key(r1, s1, z1, r2, s2, z2, n):
    """Recover private key from two signatures with same nonce"""
    # k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None
    
    k = (numerator * modinv(denominator, n)) % n
    
    # d = (s*k - z) / r mod n
    d = ((s1 * k - z1) * modinv(r1, n)) % n
    
    return d

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Parse signatures
signatures = []
for sig in instance['signatures']:
    signatures.append({
        'r': int(sig['r'], 16),
        's': int(sig['s'], 16),
        'z': int(sig['z'], 16)
    })

# Find signatures with same r value
r_groups = {}
for i, sig in enumerate(signatures):
    r = sig['r']
    if r not in r_groups:
        r_groups[r] = []
    r_groups[r].append(i)

# Find a group with at least 2 signatures
private_key = None
for r, indices in r_groups.items():
    if len(indices) >= 2:
        i1, i2 = indices[0], indices[1]
        sig1 = signatures[i1]
        sig2 = signatures[i2]
        
        private_key = recover_private_key(
            sig1['r'], sig1['s'], sig1['z'],
            sig2['r'], sig2['s'], sig2['z'],
            n
        )
        
        if private_key is not None:
            break

# Format output
result = {
    "d": format(private_key, '064x')
}

print(json.dumps(result))
