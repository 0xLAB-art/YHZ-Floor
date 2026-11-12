import base64
import re


def read_tlv(data, pos=0):
    tag = data[pos]
    pos += 1
    length = data[pos]
    pos += 1
    if length & 0x80:
        count = length & 0x7f
        length = int.from_bytes(data[pos:pos + count], 'big')
        pos += count
    end = pos + length
    return tag, data[pos:end], end


def cube_root(n):
    x = 1 << ((n.bit_length() + 2) // 3)
    while True:
        y = (2 * x + n // (x * x)) // 3
        if y >= x:
            return x
        x = y


with open('pubkey.pem', 'r') as f:
    pem = f.read()
der = base64.b64decode(''.join(
    line.strip() for line in pem.splitlines()
    if line.strip() and not line.strip().startswith('-----')
))

_, spki, _ = read_tlv(der)
_, _, pos = read_tlv(spki)
_, bit_string, _ = read_tlv(spki, pos)
assert bit_string[0] == 0
_, rsa_key, _ = read_tlv(bit_string[1:])
_, modulus_bytes, pos = read_tlv(rsa_key)
_, exponent_bytes, _ = read_tlv(rsa_key, pos)
N = int.from_bytes(modulus_bytes, 'big')
e = int.from_bytes(exponent_bytes, 'big')
assert e == 3

with open('key.enc', 'r') as f:
    Y = int(f.read().strip())
with open('file.enc', 'rb') as f:
    ciphertext = base64.b64decode(f.read())

K = cube_root(Y + N)
assert K ** 3 == Y + N
assert pow(K, e, N) == Y
assert len(ciphertext) == 64
key = K.to_bytes(64, 'big')
plaintext = bytes(c ^ k for c, k in zip(ciphertext, key))

match = re.search(rb'(?i:flag)\{[^{}\r\n]*\}', plaintext)
answer = match.group(0) if match else plaintext.rstrip(b'\x00\r\n')
answer = answer.decode('utf-8')
assert '\n' not in answer and '\r' not in answer
print(answer)
