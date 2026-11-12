import json
import sys

def modinv(a, m):
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

data = json.load(open(sys.argv[1]))

r1 = int(data['signature_1']['r'], 16)
s1 = int(data['signature_1']['s'], 16)
z1 = int(data['signature_1']['z'], 16)

r2 = int(data['signature_2']['r'], 16)
s2 = int(data['signature_2']['s'], 16)
z2 = int(data['signature_2']['z'], 16)

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

k = ((z1 - z2) * modinv(s1 - s2, n)) % n
d = ((s1 * k - z1) * modinv(r1, n)) % n

print(json.dumps({"d": f"{d:064x}", "k": f"{k:064x}"}))
