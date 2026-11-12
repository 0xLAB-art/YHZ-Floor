import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if not l.startswith('-----')]
modulus = int(''.join(lines), 16)

with open('key.enc') as f:
    y_str = f.read().strip()
Y = int(y_str)

with open('file.enc') as f:
    b64 = f.read().strip()
Y_xor_S = base64.b64decode(b64)

K = round(Y ** (1/3))
while K**3 < Y:
    K += 1
while K**3 > Y:
    K -= 1
assert K**3 == Y

Y_bytes = K.to_bytes(192, 'big')
S = bytes(a ^ b for a, b in zip(Y_bytes, Y_xor_S))
print(S.decode())
