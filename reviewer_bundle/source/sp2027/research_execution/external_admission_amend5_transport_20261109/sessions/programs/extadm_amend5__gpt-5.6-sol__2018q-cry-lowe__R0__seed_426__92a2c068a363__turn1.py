import base64
import sys


def read_tlv(data, offset):
    if offset + 2 > len(data):
        raise ValueError("Invalid DER data")
    tag = data[offset]
    offset += 1
    length = data[offset]
    offset += 1
    if length & 0x80:
        count = length & 0x7f
        if count == 0 or offset + count > len(data):
            raise ValueError("Invalid DER length")
        length = int.from_bytes(data[offset:offset + count], "big")
        offset += count
    end = offset + length
    if end > len(data):
        raise ValueError("Truncated DER data")
    return tag, data[offset:end], end


def load_public_key(filename):
    with open(filename, "r", encoding="ascii") as f:
        pem = f.read()
    encoded = "".join(
        line.strip() for line in pem.splitlines()
        if not line.strip().startswith("-----")
    )
    der = base64.b64decode(encoded, validate=True)

    tag, spki, end = read_tlv(der, 0)
    if tag != 0x30 or end != len(der):
        raise ValueError("Invalid public key")

    tag, _, offset = read_tlv(spki, 0)
    if tag != 0x30:
        raise ValueError("Invalid algorithm identifier")
    tag, bit_string, offset = read_tlv(spki, offset)
    if tag != 0x03 or not bit_string or bit_string[0] != 0:
        raise ValueError("Invalid RSA key bit string")

    tag, rsa_key, end = read_tlv(bit_string[1:], 0)
    if tag != 0x30 or end != len(bit_string) - 1:
        raise ValueError("Invalid RSA key")
    tag, modulus_bytes, offset = read_tlv(rsa_key, 0)
    if tag != 0x02:
        raise ValueError("Missing RSA modulus")
    tag, exponent_bytes, offset = read_tlv(rsa_key, offset)
    if tag != 0x02 or offset != len(rsa_key):
        raise ValueError("Missing RSA exponent")

    return int.from_bytes(modulus_bytes, "big"), int.from_bytes(exponent_bytes, "big")


def integer_cube_root(value):
    low = 0
    high = 1 << ((value.bit_length() + 2) // 3)
    while high - low > 1:
        middle = (low + high) // 2
        if middle * middle * middle <= value:
            low = middle
        else:
            high = middle
    return low


modulus, exponent = load_public_key("pubkey.pem")
if exponent != 3:
    raise ValueError("Unexpected public exponent")

with open("key.enc", "r", encoding="ascii") as f:
    encrypted_key = int(f.read().strip(), 10)

cube = encrypted_key + modulus
key_integer = integer_cube_root(cube)
if key_integer ** 3 != cube:
    raise ValueError("Encrypted key does not yield an exact cube")

with open("file.enc", "rb") as f:
    ciphertext = base64.b64decode(b"".join(f.read().split()), validate=True)

key = key_integer.to_bytes(len(ciphertext), "big")
plaintext = bytes(a ^ b for a, b in zip(ciphertext, key))
sys.stdout.write(plaintext.decode("utf-8") + "\n")
