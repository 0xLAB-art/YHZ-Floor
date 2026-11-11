import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and not l.strip().startswith('-----')]
modulus = int(''.join(lines), 16)

with open('key.enc') as f:
    Y = int(f.read().strip(), 16)

with open('file.enc') as f:
    C = base64.b64decode(f.read().strip())

# Y + N is a perfect cube; K = cbrt(Y + N)
K = round((Y + modulus) ** (1/3))
while K**3 < Y + modulus:
    K += 1
while K**3 > Y + modulus:
    K -= 1
assert K**3 == Y + modulus

Y_bytes = K.to_bytes(192, 'big')
S = bytes(a ^ b for a, b in zip(Y_bytes, C))
print(S.decode())
