import base64


def read_tlv(data, pos=0):
    tag = data[pos]
    pos += 1
    length = data[pos]
    pos += 1
    if length & 0x80:
        count = length & 0x7f
        length = int.from_bytes(data[pos:pos + count], "big")
        pos += count
    end = pos + length
    return tag, data[pos:end], end


with open("pubkey.pem", "r", encoding="ascii") as f:
    pem = "".join(line.strip() for line in f if not line.startswith("-----"))

der = base64.b64decode(pem)
tag, spki, end = read_tlv(der)
assert tag == 0x30 and end == len(der)
_, _, pos = read_tlv(spki, 0)
tag, bit_string, pos = read_tlv(spki, pos)
assert tag == 0x03 and bit_string[0] == 0
tag, rsa_key, end = read_tlv(bit_string, 1)
assert tag == 0x30 and end == len(bit_string)
tag, modulus_bytes, pos = read_tlv(rsa_key, 0)
assert tag == 0x02
N = int.from_bytes(modulus_bytes, "big")
tag, exponent_bytes, pos = read_tlv(rsa_key, pos)
assert tag == 0x02 and int.from_bytes(exponent_bytes, "big") == 3

with open("key.enc", "r", encoding="ascii") as f:
    Y = int(f.read().strip())

cube = Y + N
low = 0
high = 1 << ((cube.bit_length() + 2) // 3)
while low + 1 < high:
    middle = (low + high) // 2
    if middle * middle * middle <= cube:
        low = middle
    else:
        high = middle
K = low
assert K * K * K == cube

with open("file.enc", "rb") as f:
    ciphertext = base64.b64decode(f.read())

key = K.to_bytes(64, "big")
plaintext = bytes(a ^ b for a, b in zip(ciphertext, key))
print(plaintext.decode("utf-8"))
