import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and not l.strip().startswith('-----')]
keydata = ''.join(lines)
bits = int(keydata, 16)
n = 1
while bits:
    n <<= 1
    n |= bits & 1
    bits >>= 1

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

s = bytes(a ^ b for a, b in zip(k.to_bytes(64, 'big'), c))
print(s.decode('utf-8', errors='replace'))