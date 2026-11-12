import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and not l.startswith('-----')]
keydata = b''.join(base64.b64decode(l) for l in lines)

n = int.from_bytes(keydata, 'big')
e = 3

with open('key.enc') as f:
    y = int(f.read().strip())

with open('file.enc') as f:
    c = base64.b64decode(f.read().strip())

# Y + N is a perfect cube: K^3 = Y + N
val = y + n
k = round(val ** (1/3))
while k**3 < val:
    k += 1
while k**3 > val:
    k -= 1
assert k**3 == val, 'cube root failed'

# Y = K^e mod N = K^3 mod N; recover Y mod N
y_mod = k**3 % n

# C = Y xor S  =>  S = C xor Y
s = bytes(a ^ b for a, b in zip(c, y_mod.to_bytes(len(c), 'big')))

print(s.decode('utf-8', errors='replace'))