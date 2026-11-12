import base64


def read_text(path):
    with open(path, "r", encoding="ascii") as handle:
        return handle.read()


def der_item(data, offset):
    if offset + 2 > len(data):
        raise ValueError("Truncated DER item")

    tag = data[offset]
    offset += 1
    first_length = data[offset]
    offset += 1

    if first_length & 0x80:
        length_bytes = first_length & 0x7f
        if length_bytes == 0 or offset + length_bytes > len(data):
            raise ValueError("Invalid DER length")
        length = int.from_bytes(data[offset:offset + length_bytes], "big")
        offset += length_bytes
    else:
        length = first_length

    end = offset + length
    if end > len(data):
        raise ValueError("Truncated DER value")
    return tag, data[offset:end], end


def load_public_key(path):
    pem = read_text(path)
    encoded = "".join(
        line.strip()
        for line in pem.splitlines()
        if line.strip() and not line.strip().startswith("-----")
    )
    der = base64.b64decode(encoded, validate=True)

    tag, spki, end = der_item(der, 0)
    if tag != 0x30 or end != len(der):
        raise ValueError("Invalid SubjectPublicKeyInfo")

    algorithm_tag, _, position = der_item(spki, 0)
    bit_string_tag, bit_string, position = der_item(spki, position)
    if algorithm_tag != 0x30 or bit_string_tag != 0x03 or position != len(spki):
        raise ValueError("Invalid RSA public key")
    if not bit_string or bit_string[0] != 0:
        raise ValueError("Invalid DER bit string")

    tag, rsa_key, end = der_item(bit_string[1:], 0)
    if tag != 0x30 or end != len(bit_string) - 1:
        raise ValueError("Invalid PKCS#1 public key")

    modulus_tag, modulus_bytes, position = der_item(rsa_key, 0)
    exponent_tag, exponent_bytes, position = der_item(rsa_key, position)
    if modulus_tag != 0x02 or exponent_tag != 0x02 or position != len(rsa_key):
        raise ValueError("Invalid RSA integers")

    return int.from_bytes(modulus_bytes, "big"), int.from_bytes(exponent_bytes, "big")


def integer_cube_root(value):
    low = 0
    high = 1 << ((value.bit_length() + 2) // 3)
    while high * high * high <= value:
        high <<= 1

    while low + 1 < high:
        middle = (low + high) // 2
        cube = middle * middle * middle
        if cube <= value:
            low = middle
        else:
            high = middle
    return low


def main():
    modulus, exponent = load_public_key("pubkey.pem")
    if exponent != 3:
        raise ValueError("Unexpected RSA exponent")

    encrypted_key = int(read_text("key.enc").strip())
    key = integer_cube_root(encrypted_key + modulus)
    if key ** 3 != encrypted_key + modulus or pow(key, exponent, modulus) != encrypted_key:
        raise ValueError("RSA ciphertext does not have the required cube relation")

    encoded_ciphertext = "".join(read_text("file.enc").split())
    ciphertext = base64.b64decode(encoded_ciphertext, validate=True)
    if len(ciphertext) != 64 or key.bit_length() > 512:
        raise ValueError("Unexpected key or ciphertext size")

    key_bytes = key.to_bytes(64, "big")
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, key_bytes))
    result = plaintext.decode("ascii")
    if "\n" in result or "\r" in result:
        raise ValueError("Recovered answer is not a single line")
    print(result)


if __name__ == "__main__":
    main()
