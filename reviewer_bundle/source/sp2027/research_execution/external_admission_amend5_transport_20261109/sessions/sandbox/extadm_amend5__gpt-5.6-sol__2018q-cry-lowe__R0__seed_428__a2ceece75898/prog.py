import base64
import sys


def read_der_item(data, offset=0):
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


def load_modulus(path):
    with open(path, "r", encoding="ascii") as handle:
        pem = handle.read()
    encoded = "".join(
        line.strip() for line in pem.splitlines()
        if not line.startswith("-----")
    )
    der = base64.b64decode(encoded)

    outer_tag, outer, _ = read_der_item(der)
    assert outer_tag == 0x30
    _, _, offset = read_der_item(outer, 0)
    bit_tag, bit_string, _ = read_der_item(outer, offset)
    assert bit_tag == 0x03 and bit_string[0] == 0

    rsa_tag, rsa_key, _ = read_der_item(bit_string, 1)
    assert rsa_tag == 0x30
    modulus_tag, modulus_bytes, _ = read_der_item(rsa_key, 0)
    assert modulus_tag == 0x02
    return int.from_bytes(modulus_bytes, "big")


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


modulus = load_modulus("pubkey.pem")
with open("key.enc", "r", encoding="ascii") as handle:
    encrypted_key = int(handle.read().strip())

cube = encrypted_key + modulus
key = integer_cube_root(cube)
assert key * key * key == cube

with open("file.enc", "rb") as handle:
    ciphertext = base64.b64decode(handle.read().strip())

key_bytes = key.to_bytes(len(ciphertext), "big")
plaintext = bytes(a ^ b for a, b in zip(ciphertext, key_bytes))
sys.stdout.buffer.write(plaintext + b"\n")
