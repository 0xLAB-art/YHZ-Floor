import base64
import json
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and not l.startswith('-----')]
keydata = ''.join(lines)
modulus = int(keydata, 16)

with open('key.enc') as f:
    y = int(f.read().strip())

with open('file.enc') as f:
    c = base64.b64decode(f.read().strip())

k = round(y ** (1/3))
for cand in (k-1, k, k+1):
    if cand**3 == y:
        k = cand
        break

y_bytes = k.to_bytes(192, 'big')
flag = bytes(a ^ b for a, b in zip(y_bytes, c))
print(flag.decode('utf-8', errors='replace'))
