import json
import sys

def modinv(a, m):
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = egcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = egcd(a % m, m)
    if gcd != 1:
        raise Exception('Modular inverse does not exist')
    return (x % m + m) % m

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

r = int(data['signature_1']['r'], 16)
s1 = int(data['signature_1']['s'], 16)
z1 = int(data['signature_1']['z'], 16)
s2 = int(data['signature_2']['s'], 16)
z2 = int(data['signature_2']['z'], 16)

k = ((z1 - z2) * modinv(s1 - s2, n)) % n
d = ((s1 * k - z1) * modinv(r, n)) % n

print(json.dumps({"d": f"{d:064x}", "k": f"{k:064x}"}))
