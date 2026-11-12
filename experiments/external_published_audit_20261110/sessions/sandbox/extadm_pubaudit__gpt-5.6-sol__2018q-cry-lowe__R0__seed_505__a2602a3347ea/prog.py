import base64
import sys


def read_tlv(data, pos):
    tag = data[pos]
    pos += 1
    first = data[pos]
    pos += 1
    if first & 0x80:
        count = first & 0x7f
        if count == 0 or pos + count > len(data):
            raise ValueError("Invalid DER length")
        length = int.from_bytes(data[pos:pos + count], "big")
        pos += count
    else:
        length = first
    end = pos + length
    if end > len(data):
        raise ValueError("Truncated DER value")
    return tag, data[pos:end], end


def read_public_key(path):
    with open(path, "r", encoding="ascii") as handle:
        lines = handle.read().splitlines()
    encoded = "".join(line.strip() for line in lines if not line.startswith("-----"))
    der = base64.b64decode(encoded)

    tag, spki, end = read_tlv(der, 0)
    if tag != 0x30 or end != len(der):
        raise ValueError("Invalid SubjectPublicKeyInfo")

    tag, _, pos = read_tlv(spki, 0)
    if tag != 0x30:
        raise ValueError("Invalid algorithm identifier")
    tag, bit_string, pos = read_tlv(spki, pos)
    if tag != 0x03 or not bit_string or bit_string[0] != 0 or pos != len(spki):
        raise ValueError("Invalid RSA public-key bit string")

    rsa_der = bit_string[1:]
    tag, rsa_sequence, end = read_tlv(rsa_der, 0)
    if tag != 0x30 or end != len(rsa_der):
        raise ValueError("Invalid RSA public key")

    tag, modulus_bytes, pos = read_tlv(rsa_sequence, 0)
    if tag != 0x02:
        raise ValueError("Missing RSA modulus")
    tag, exponent_bytes, pos = read_tlv(rsa_sequence, pos)
    if tag != 0x02 or pos != len(rsa_sequence):
        raise ValueError("Missing RSA exponent")

    return int.from_bytes(modulus_bytes, "big"), int.from_bytes(exponent_bytes, "big")


def exact_cube_root(value):
    low = 0
    high = 1 << ((value.bit_length() + 2) // 3)
    while low + 1 < high:
        middle = (low + high) // 2
        if middle * middle * middle <= value:
            low = middle
        else:
            high = middle
    if low * low * low != value:
        raise ValueError("Value is not a perfect cube")
    return low


modulus, exponent = read_public_key("pubkey.pem")
if exponent != 3:
    raise ValueError("Unexpected RSA exponent")

with open("key.enc", "r", encoding="ascii") as handle:
    encrypted_key = int(handle.read().strip(), 10)

symmetric_key = exact_cube_root(encrypted_key + modulus)

with open("file.enc", "rb") as handle:
    ciphertext = base64.b64decode(handle.read())

key_bytes = symmetric_key.to_bytes(len(ciphertext), "big")
plaintext = bytes(a ^ b for a, b in zip(ciphertext, key_bytes)).decode("utf-8")
if "\n" in plaintext or "\r" in plaintext:
    raise ValueError("Recovered flag is not a single line")
sys.stdout.write(plaintext + "\n")
