import sys
import json

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def recover_private_key(sig1, sig2, n):
    """Recover private key from two signatures with same k"""
    r1 = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    
    r2 = int(sig2['r'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Verify same r value
    assert r1 == r2, "Signatures must have same r"
    r = r1
    
    # Calculate k = (z1 - z2) / (s1 - s2) mod n
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    k = (numerator * modinv(denominator, n)) % n
    
    # Calculate d = (s*k - z) / r mod n
    numerator_d = (s1 * k - z1) % n
    d = (numerator_d * modinv(r, n)) % n
    
    return d, k

# secp256k1 curve order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Read instance
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

signatures = data['signatures']

# Find signatures with same r (indices 13 and 15)
d, k = recover_private_key(signatures[13], signatures[15], n)

# Format as 64 lowercase hex characters
d_hex = format(d, '064x')
k_hex = format(k, '064x')

result = {
    "d": d_hex,
    "k": k_hex
}

print(json.dumps(result))
