import base64


def read_tlv(data, pos=0):
    tag = data[pos]
    pos += 1
    first = data[pos]
    pos += 1
    if first & 0x80:
        count = first & 0x7f
        length = int.from_bytes(data[pos:pos + count], "big")
        pos += count
    else:
        length = first
    end = pos + length
    return tag, data[pos:end], end


with open("pubkey.pem", "r", encoding="ascii") as f:
    pem = f.read()

der = base64.b64decode("".join(
    line.strip() for line in pem.splitlines() if not line.startswith("-----")
))

_, spki, _ = read_tlv(der)
_, _, offset = read_tlv(spki, 0)
_, bit_string, _ = read_tlv(spki, offset)
_, rsa_key, _ = read_tlv(bit_string[1:], 0)
_, modulus_bytes, _ = read_tlv(rsa_key, 0)
modulus = int.from_bytes(modulus_bytes, "big")

with open("key.enc", "r", encoding="ascii") as f:
    y = int(f.read().strip())


def integer_cube_root(value):
    low = 0
    high = 1 << ((value.bit_length() + 2) // 3)
    while low + 1 < high:
        middle = (low + high) // 2
        if middle * middle * middle <= value:
            low = middle
        else:
            high = middle
    return low


k = integer_cube_root(y + modulus)
assert k ** 3 == y + modulus
key = k.to_bytes(64, "big")

with open("file.enc", "rb") as f:
    ciphertext = base64.b64decode(f.read())

assert len(ciphertext) == len(key) == 64
flag = bytes(a ^ b for a, b in zip(ciphertext, key))
print(flag.decode("utf-8"))
