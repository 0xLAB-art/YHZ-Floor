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
    return (x % m + m) % m

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

r = int(data['signature_1']['r'], 16)
s1 = int(data['signature_1']['s'], 16)
z1 = int(data['signature_1']['z'], 16)
s2 = int(data['signature_2']['s'], 16)
z2 = int(data['signature_2']['z'], 16)

k = ((z1 - z2) * modinv(s1 - s2, N)) % N
d = ((s1 * k - z1) * modinv(r, N)) % N

print(json.dumps({"d": format(d, '064x'), "k": format(k, '064x')}))
