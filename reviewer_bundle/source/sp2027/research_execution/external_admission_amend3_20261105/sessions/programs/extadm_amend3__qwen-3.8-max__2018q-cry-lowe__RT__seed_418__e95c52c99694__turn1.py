import base64

with open('pubkey.pem', 'rb') as f:
    pem = f.read()
lines = [l for l in pem.split(b'\n') if l and not l.startswith(b'-----')]
der = base64.b64decode(b''.join(lines))
# SubjectPublicKeyInfo: SEQUENCE { SEQUENCE { OID }, BIT STRING { modulus, exponent } }
assert der[0] == 0x30
_, rest = int.from_bytes(der[1:2], 'big'), der[2:]
assert rest[0] == 0x30
_, rest = int.from_bytes(rest[1:2], 'big'), rest[1:]
assert rest[0] == 0x06 and rest[1] == 0x09
_, rest = int.from_bytes(rest[2:2+rest[1]], 'big'), rest[2+rest[1]+1]
assert rest[0] == 0x03
_, rest = int.from_bytes(rest[1:2], 'big'), rest[2:]
assert rest[0] == 0x02
n_len = int.from_bytes(rest[1:2], 'big'); rest = rest[2:]
n = int.from_bytes(rest[:n_len], 'big'); rest = rest[n_len:]
assert rest[0] == 0x02
e = int.from_bytes(rest[1:], 'big')

with open('key.enc', 'rb') as f:
    y = int(f.read().strip())
with open('file.enc', 'rb') as f:
    c = base64.b64decode(f.read().strip())

# Y + N is a perfect cube: K^3 = Y + N
val = y + n
k = round(val ** (1/3))
while k**3 < val:
    k += 1
while k**3 > val:
    k -= 1
assert k**3 == val

# K is 512-bit; Y = K^e mod N stored big-endian, 192 bytes
k_bytes = k.to_bytes(64, 'big')
key = k_bytes[:len(c)]
flag = bytes(a ^ b for a, b in zip(c, key))
print(flag.decode('utf-8', errors='replace'))
