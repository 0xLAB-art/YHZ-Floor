import base64


def read_tlv(data, offset=0):
    if offset + 2 > len(data):
        raise ValueError("truncated DER")
    tag = data[offset]
    offset += 1
    length = data[offset]
    offset += 1
    if length & 0x80:
        count = length & 0x7f
        if count == 0 or offset + count > len(data):
            raise ValueError("invalid DER length")
        length = int.from_bytes(data[offset:offset + count], "big")
        offset += count
    end = offset + length
    if end > len(data):
        raise ValueError("truncated DER value")
    return tag, data[offset:end], end


def load_public_key(path):
    with open(path, "rb") as f:
        pem = f.read()
    encoded = b"".join(
        line.strip() for line in pem.splitlines()
        if not line.startswith(b"-----")
    )
    der = base64.b64decode(encoded, validate=True)

    tag, spki, end = read_tlv(der)
    if tag != 0x30 or end != len(der):
        raise ValueError("invalid SubjectPublicKeyInfo")

    tag, _, offset = read_tlv(spki, 0)
    if tag != 0x30:
        raise ValueError("invalid algorithm identifier")
    tag, bit_string, offset = read_tlv(spki, offset)
    if tag != 0x03 or offset != len(spki) or not bit_string or bit_string[0] != 0:
        raise ValueError("invalid public-key bit string")

    tag, rsa_key, end = read_tlv(bit_string[1:], 0)
    if tag != 0x30 or end != len(bit_string) - 1:
        raise ValueError("invalid RSA public key")
    tag, modulus_bytes, offset = read_tlv(rsa_key, 0)
    if tag != 0x02:
        raise ValueError("missing RSA modulus")
    tag, exponent_bytes, offset = read_tlv(rsa_key, offset)
    if tag != 0x02 or offset != len(rsa_key):
        raise ValueError("missing RSA exponent")

    return int.from_bytes(modulus_bytes, "big"), int.from_bytes(exponent_bytes, "big")


def integer_cube_root(value):
    x = 1 << ((value.bit_length() + 2) // 3)
    while True:
        next_x = (2 * x + value // (x * x)) // 3
        if next_x >= x:
            return x
        x = next_x


modulus, exponent = load_public_key("pubkey.pem")
if exponent != 3:
    raise ValueError("unexpected RSA exponent")

with open("key.enc", "r", encoding="ascii") as f:
    encrypted_key = int(f.read().strip())

key = integer_cube_root(encrypted_key + modulus)
if key ** 3 != encrypted_key + modulus:
    raise ValueError("RSA ciphertext does not yield an exact cube")

with open("file.enc", "rb") as f:
    ciphertext = base64.b64decode(f.read().strip(), validate=True)

key_bytes = key.to_bytes(len(ciphertext), "big")
plaintext = bytes(a ^ b for a, b in zip(ciphertext, key_bytes))
print(plaintext.decode("utf-8"))
