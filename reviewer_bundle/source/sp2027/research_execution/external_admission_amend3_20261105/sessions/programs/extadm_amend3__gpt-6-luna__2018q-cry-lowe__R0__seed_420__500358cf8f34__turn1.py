import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if not l.startswith('-----')]
der = ''.join(lines)
N = int(der, 16)

with open('key.enc') as f:
    Y = int(f.read().strip())

with open('file.enc') as f:
    C = base64.b64decode(f.read().strip())

K = round((Y + N) ** (1/3))
while K**3 != Y + N:
    K += 1

Y_bytes = Y.to_bytes(192, 'big')
key = bytes(a ^ b for a, b in zip(Y_bytes, C))

print(key.decode('utf-8', errors='replace'))