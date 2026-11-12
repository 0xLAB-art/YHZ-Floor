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


with open("pubkey.pem", "rb") as f:
    pem = f.read()
body = b"".join(
    line.strip() for line in pem.splitlines()
    if not line.startswith(b"-----")
)
der = base64.b64decode(body)

_, spki, _ = read_tlv(der)
_, _, pos = read_tlv(spki)
_, bit_string, _ = read_tlv(spki, pos)
if not bit_string or bit_string[0] != 0:
    raise ValueError("Invalid RSA public key")
_, rsa_key, _ = read_tlv(bit_string, 1)
_, modulus_bytes, pos = read_tlv(rsa_key)
_, exponent_bytes, _ = read_tlv(rsa_key, pos)
N = int.from_bytes(modulus_bytes, "big")
e = int.from_bytes(exponent_bytes, "big")
if e != 3:
    raise ValueError("Unexpected public exponent")

with open("key.enc", "r", encoding="ascii") as f:
    Y = int(f.read().strip())

cube = Y + N
low = 0
high = 1 << ((cube.bit_length() + 2) // 3)
while high - low > 1:
    mid = (low + high) // 2
    if mid * mid * mid <= cube:
        low = mid
    else:
        high = mid
K = low
if K * K * K != cube:
    raise ValueError("Y + N is not a perfect cube")

with open("file.enc", "rb") as f:
    ciphertext = base64.b64decode(f.read())
key_bytes = K.to_bytes(len(ciphertext), "big")
plaintext = bytes(a ^ b for a, b in zip(ciphertext, key_bytes))
text = plaintext.decode("utf-8")
if "\n" in text or "\r" in text:
    raise ValueError("Recovered flag is not one line")
print(text)
