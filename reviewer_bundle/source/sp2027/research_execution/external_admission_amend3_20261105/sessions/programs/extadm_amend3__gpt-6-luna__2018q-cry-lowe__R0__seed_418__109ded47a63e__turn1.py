import base64
import math

with open("pubkey.pem") as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and "-----" not in l]
modulus = int("".join(lines), 16)

with open("key.enc") as f:
    y = int(f.read().strip())

with open("file.enc") as f:
    c = base64.b64decode(f.read().strip())

# Y + N is a perfect cube: K^3 = Y + N
k = round((y + modulus) ** (1/3))
while k**3 < y + modulus:
    k += 1
while k**3 > y + modulus:
    k -= 1
assert k**3 == y + modulus

# Y = K^e mod N = K^3 mod N, so Y = K^3 - N (since K^3 < 2N)
# C = Y xor S  =>  S = C xor Y
y_bytes = y.to_bytes((y.bit_length() + 7) // 8, "big")
s = bytes(a ^ b for a, b in zip(c, y_bytes))
print(s.decode())
