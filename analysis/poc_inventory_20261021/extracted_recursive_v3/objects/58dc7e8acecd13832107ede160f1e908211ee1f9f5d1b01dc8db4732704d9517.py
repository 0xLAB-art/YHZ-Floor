import sys
import json

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = egcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = egcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

# Read instance
with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

# secp256k1 parameters
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

signatures = instance['signatures']

# Convert hex to int
sigs = []
for sig in signatures:
    sigs.append({
        'r': int(sig['r'], 16),
        's': int(sig['s'], 16),
        'z': int(sig['z'], 16)
    })

# Find duplicate r values
r_map = {}
for i, sig in enumerate(sigs):
    r = sig['r']
    if r not in r_map:
        r_map[r] = []
    r_map[r].append(i)

# Find pair with same r
d = None
for r, indices in r_map.items():
    if len(indices) >= 2:
        i1, i2 = indices[0], indices[1]
        s1, z1 = sigs[i1]['s'], sigs[i1]['z']
        s2, z2 = sigs[i2]['s'], sigs[i2]['z']
        
        # Recover k: k = (z1 - z2) / (s1 - s2) mod n
        k = ((z1 - z2) * modinv((s1 - s2) % n, n)) % n
        
        # Recover d: d = (s*k - z) / r mod n
        d = ((s1 * k - z1) * modinv(r, n)) % n
        break

# Output result
result = {'d': format(d, '064x')}
print(json.dumps(result))