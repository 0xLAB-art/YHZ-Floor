import sys
import json
import base64

def b64_to_int(s):
    return int.from_bytes(base64.b64decode(s), 'big')

def mod_inverse(a, m):
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

r = b64_to_int(data['signature_1']['r'])
s1 = b64_to_int(data['signature_1']['s'])
z1 = b64_to_int(data['signature_1']['z'])
s2 = b64_to_int(data['signature_2']['s'])
z2 = b64_to_int(data['signature_2']['z'])

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

k = ((z1 - z2) * mod_inverse(s1 - s2, n)) % n
d = ((s1 * k - z1) * mod_inverse(r, n)) % n

print(json.dumps({"d": f"{d:064x}", "k": f"{k:064x}"}))
