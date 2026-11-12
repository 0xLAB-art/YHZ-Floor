import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and not l.startswith('-----')]
keydata = ''.join(lines)
modulus = int(base64.b64decode(keydata), 16)

with open('key.enc') as f:
    Y = int(f.read().strip())

with open('file.enc') as f:
    C = base64.b64decode(f.read().strip())

K = round(Y ** (1/3))
while K**3 < Y:
    K += 1
while K**3 > Y:
    K -= 1
assert K**3 == Y, 'cube root failed'

Y_bytes = K.to_bytes((Y.bit_length() + 7) // 8, 'big')
flag = bytes(a ^ b for a, b in zip(C, Y_bytes))
print(flag.decode())
