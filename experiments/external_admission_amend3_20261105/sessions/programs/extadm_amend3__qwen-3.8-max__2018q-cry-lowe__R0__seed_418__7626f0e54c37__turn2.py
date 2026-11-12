import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if not l.startswith('-----')]
modulus = int(''.join(lines), 16)

with open('key.enc') as f:
    y = int(f.read().strip())

with open('file.enc') as f:
    c = base64.b64decode(f.read().strip())

k = round(y ** (1/3))
while k**3 < y:
    k += 1
while k**3 > y:
    k -= 1
assert k**3 == y

y_bytes = k.to_bytes(192, 'big')
flag = bytes(a ^ b for a, b in zip(y_bytes, c))
print(flag.decode())
