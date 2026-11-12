import base64

with open('pubkey.pem', 'rb') as f:
    pem = f.read()
lines = [l for l in pem.split(b'\n') if l and not l.startswith(b'-----')]
der = base64.b64decode(b''.join(lines))
# SubjectPublicKeyInfo: SEQUENCE { SEQUENCE { OID, NULL }, BIT STRING }
assert der[0] == 0x30
_, rest = int.from_bytes(der[1:2], 'big'), der[2:]
assert rest[0] == 0x30
_, rest = int.from_bytes(rest[1:2], 'big'), rest[1:]
# skip OID
_, rest = int.from_bytes(rest[1:2], 'big'), rest[1:]
assert rest[0] == 0x06
_, rest = int.from_bytes(rest[1:2], 'big'), rest[1:]
assert rest[:9] == b'\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01'
_, rest = int.from_bytes(rest[9:10], 'big'), rest[10:]
assert rest[0] == 0x05
_, rest = int.from_bytes(rest[1:2], 'big'), rest[1:]
assert rest[0] == 0x00
_, rest = int.from_bytes(rest[1:2], 'big'), rest[1:]
assert rest[0] == 0x03
_, rest = int.from_bytes(rest[1:2], 'big'), rest[1:]
assert rest[0] == 0x00
_, rest = int.from_bytes(rest[1:2], 'big'), rest[1:]
assert rest[0] == 0x01
assert rest[1:3] == b'\x01\x00'
_, rest = int.from_bytes(rest[3:4], 'big'), rest[4:]
assert rest[0] == 0x04
_, rest = int.from_bytes(rest[1:2], 'big'), rest[1:]
assert rest[0] == 0x02
_, nlen = int.from_bytes(rest[1:2], 'big'), rest[2:]
assert rest[2 + nlen] == 0x02
_, elen = int.from_bytes(rest[2 + nlen + 1:2 + nlen + 2], 'big'), rest[2 + nlen + 3:]
N = int.from_bytes(nlen, 'big')
e = elen

with open('key.enc', 'rb') as f:
    y = int.from_bytes(f.read(), 'big')
with open('file.enc', 'rb') as f:
    c = base64.b64decode(f.read())

# Y + N = K^3
k = round((y + N) ** (1 / 3))
while k ** 3 < y + N:
    k += 1
while k ** 3 > y + N:
    k -= 1
assert k ** 3 == y + N
Y = k ** 3 - N
assert Y == y

key = Y.to_bytes(192, 'big')
flag = bytes(a ^ b for a, b in zip(c, key))
print(flag.decode())
