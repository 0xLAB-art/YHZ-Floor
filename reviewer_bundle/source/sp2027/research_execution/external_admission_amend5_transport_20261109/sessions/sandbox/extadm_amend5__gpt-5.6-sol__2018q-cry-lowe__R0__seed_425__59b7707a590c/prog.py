import base64
import sys


def read_tlv(data, pos):
    if pos >= len(data):
        raise ValueError("truncated DER")
    tag = data[pos]
    pos += 1
    if pos >= len(data):
        raise ValueError("truncated DER length")
    length = data[pos]
    pos += 1
    if length & 0x80:
        count = length & 0x7f
        if count == 0 or pos + count > len(data):
            raise ValueError("invalid DER length")
        length = int.from_bytes(data[pos:pos + count], "big")
        pos += count
    end = pos + length
    if end > len(data):
        raise ValueError("truncated DER value")
    return tag, data[pos:end], end


def load_public_key(path):
    with open(path, "r", encoding="ascii") as f:
        pem = f.read()
    body = "".join(
        line.strip() for line in pem.splitlines()
        if not line.startswith("-----")
    )
    der = base64.b64decode(body, validate=True)

    tag, spki, end = read_tlv(der, 0)
    if tag != 0x30 or end != len(der):
        raise ValueError("invalid public key")

    tag, _, pos = read_tlv(spki, 0)
    if tag != 0x30:
        raise ValueError("invalid algorithm identifier")
    tag, bit_string, pos = read_tlv(spki, pos)
    if tag != 0x03 or pos != len(spki) or not bit_string or bit_string[0] != 0:
        raise ValueError("invalid RSA bit string")

    tag, rsa_key, end = read_tlv(bit_string[1:], 0)
    if tag != 0x30 or end != len(bit_string) - 1:
        raise ValueError("invalid RSA public key")

    tag, modulus_bytes, pos = read_tlv(rsa_key, 0)
    if tag != 0x02:
        raise ValueError("missing RSA modulus")
    tag, exponent_bytes, pos = read_tlv(rsa_key, pos)
    if tag != 0x02 or pos != len(rsa_key):
        raise ValueError("missing RSA exponent")

    return int.from_bytes(modulus_bytes, "big"), int.from_bytes(exponent_bytes, "big")


def exact_cube_root(value):
    low = 0
    high = 1 << ((value.bit_length() + 2) // 3)
    while low <= high:
        middle = (low + high) // 2
        cube = middle * middle * middle
        if cube == value:
            return middle
        if cube < value:
            low = middle + 1
        else:
            high = middle - 1
    raise ValueError("value is not a perfect cube")


modulus, exponent = load_public_key("pubkey.pem")
if exponent != 3:
    raise ValueError("unexpected RSA exponent")

with open("key.enc", "r", encoding="ascii") as f:
    encrypted_key = int(f.read().strip(), 10)

with open("file.enc", "r", encoding="ascii") as f:
    ciphertext = base64.b64decode("".join(f.read().split()), validate=True)

key_integer = exact_cube_root(encrypted_key + modulus)
if key_integer.bit_length() > 8 * len(ciphertext):
    raise ValueError("recovered key is too large")
key = key_integer.to_bytes(len(ciphertext), "big")
plaintext = bytes(a ^ b for a, b in zip(ciphertext, key))
if b"\n" in plaintext or b"\r" in plaintext:
    raise ValueError("plaintext is not a single line")
sys.stdout.buffer.write(plaintext + b"\n")
