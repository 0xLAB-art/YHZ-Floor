import base64
import math

with open('pubkey.pem', 'rb') as f:
    pem = f.read()
lines = [l for l in pem.split(b'\n') if l and not l.startswith(b'-----')]
modulus = int(''.join(lines).decode(), 16)

with open('key.enc', 'rb') as f:
    Y = int(f.read().decode().strip(), 10)

with open('file.enc', 'rb') as f:
    C = base64.b64decode(f.read())

K = round((Y + modulus) ** (1/3))
while K**3 < Y + modulus:
    K += 1
while K**3 > Y + modulus:
    K -= 1
assert K**3 == Y + modulus

Y_bytes = K.to_bytes((Y.bit_length() + 7) // 8, 'big')
S = bytes(a ^ b for a, b in zip(C, Y_bytes))
print(S.decode())
