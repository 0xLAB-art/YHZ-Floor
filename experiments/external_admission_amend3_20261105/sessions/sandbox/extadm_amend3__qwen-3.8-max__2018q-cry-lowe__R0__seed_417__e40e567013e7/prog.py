import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if not l.startswith('-----')]
modulus = int(''.join(lines), 16)

with open('key.enc') as f:
    y_str = f.read().strip()
y = int(y_str)

with open('file.enc') as f:
    b64 = f.read().strip()
y_xor = base64.b64decode(b64)

k = round(y ** (1/3))
while k**3 < y:
    k += 1
while k**3 > y:
    k -= 1
assert k**3 == y

y_bytes = k.to_bytes(192, 'big')
secret = bytes(a ^ b for a, b in zip(y_bytes, y_xor))
print(secret.decode())