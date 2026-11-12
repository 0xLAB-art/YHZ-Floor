import base64
import sys


def read_tlv(data, offset=0):
    tag = data[offset]
    offset += 1
    length = data[offset]
    offset += 1
    if length & 0x80:
        count = length & 0x7f
        length = int.from_bytes(data[offset:offset + count], "big")
        offset += count
    end = offset + length
    return tag, data[offset:end], end


def read_public_key(path):
    with open(path, "r", encoding="ascii") as f:
        lines = f.read().splitlines()
    body = "".join(line.strip() for line in lines if not line.startswith("-----"))
    der = base64.b64decode(body)

    tag, spki, end = read_tlv(der)
    if tag != 0x30 or end != len(der):
        raise ValueError("Invalid public key")

    tag, _, offset = read_tlv(spki, 0)
    if tag != 0x30:
        raise ValueError("Invalid algorithm identifier")
    tag, bit_string, offset = read_tlv(spki, offset)
    if tag != 0x03 or not bit_string or bit_string[0] != 0:
        raise ValueError("Invalid RSA key bit string")

    tag, rsa_key, end = read_tlv(bit_string, 1)
    if tag != 0x30:
        raise ValueError("Invalid RSA public key")
    tag, modulus_bytes, offset = read_tlv(rsa_key, 0)
    if tag != 0x02:
        raise ValueError("Missing RSA modulus")
    tag, exponent_bytes, offset = read_tlv(rsa_key, offset)
    if tag != 0x02:
        raise ValueError("Missing RSA exponent")

    modulus = int.from_bytes(modulus_bytes, "big")
    exponent = int.from_bytes(exponent_bytes, "big")
    return modulus, exponent


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


modulus, exponent = read_public_key("pubkey.pem")
if exponent != 3:
    raise ValueError("Unexpected public exponent")

with open("key.enc", "r", encoding="ascii") as f:
    encrypted_key = int(f.read().strip())

key_integer = integer_cube_root(encrypted_key + modulus)
if key_integer ** 3 != encrypted_key + modulus:
    raise ValueError("Recovered value is not an exact cube")

with open("file.enc", "rb") as f:
    ciphertext = base64.b64decode(f.read(), validate=True)

key = key_integer.to_bytes(64, "big")
if len(ciphertext) != len(key):
    raise ValueError("Unexpected ciphertext length")

plaintext = bytes(a ^ b for a, b in zip(ciphertext, key))
sys.stdout.write(plaintext.decode("utf-8") + "\n")
