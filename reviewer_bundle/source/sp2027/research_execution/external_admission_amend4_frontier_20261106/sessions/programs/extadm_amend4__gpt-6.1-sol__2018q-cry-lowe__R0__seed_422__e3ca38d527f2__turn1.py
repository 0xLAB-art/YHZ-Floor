import base64


def read_tlv(data, offset=0):
    tag = data[offset]
    offset += 1
    length = data[offset]
    offset += 1
    if length & 0x80:
        count = length & 0x7f
        length = int.from_bytes(data[offset:offset + count], 'big')
        offset += count
    end = offset + length
    return tag, data[offset:end], end


def integer_cube_root(value):
    low = 0
    high = 1 << ((value.bit_length() + 2) // 3)
    while low + 1 < high:
        middle = (low + high) // 2
        if middle ** 3 <= value:
            low = middle
        else:
            high = middle
    return low


with open('pubkey.pem', 'r', encoding='ascii') as f:
    pem = f.read()
der = base64.b64decode(''.join(
    line.strip() for line in pem.splitlines()
    if line.strip() and not line.startswith('-----')
))

_, outer, _ = read_tlv(der)
_, _, position = read_tlv(outer)
_, bit_string, _ = read_tlv(outer, position)
assert bit_string[0] == 0
_, rsa_key, _ = read_tlv(bit_string[1:])
_, modulus_bytes, position = read_tlv(rsa_key)
_, exponent_bytes, _ = read_tlv(rsa_key, position)
modulus = int.from_bytes(modulus_bytes, 'big')
exponent = int.from_bytes(exponent_bytes, 'big')
assert exponent == 3

with open('key.enc', 'r', encoding='ascii') as f:
    encrypted_key = int(f.read().strip())
with open('file.enc', 'r', encoding='ascii') as f:
    ciphertext = base64.b64decode(f.read())

cube = encrypted_key + modulus
key = integer_cube_root(cube)
assert key ** 3 == cube
assert len(ciphertext) == 64
key_bytes = key.to_bytes(64, 'big')
plaintext = bytes(c ^ k for c, k in zip(ciphertext, key_bytes))
print(plaintext.decode('utf-8'))
