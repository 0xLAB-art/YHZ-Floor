import base64


def read_tlv(data, pos):
    tag = data[pos]
    pos += 1
    length = data[pos]
    pos += 1
    if length & 0x80:
        count = length & 0x7f
        length = int.from_bytes(data[pos:pos + count], "big")
        pos += count
    end = pos + length
    if end > len(data):
        raise ValueError("Invalid DER data")
    return tag, pos, end, end


def read_public_key(path):
    with open(path, "r", encoding="ascii") as f:
        pem = f.read()
    encoded = "".join(
        line.strip() for line in pem.splitlines()
        if not line.startswith("-----")
    )
    der = base64.b64decode(encoded)

    tag, outer_start, outer_end, _ = read_tlv(der, 0)
    if tag != 0x30 or outer_end != len(der):
        raise ValueError("Invalid public key")

    tag, _, _, pos = read_tlv(der, outer_start)
    if tag != 0x30:
        raise ValueError("Invalid algorithm identifier")

    tag, bit_start, bit_end, _ = read_tlv(der, pos)
    if tag != 0x03 or der[bit_start] != 0:
        raise ValueError("Invalid RSA bit string")
    rsa = der[bit_start + 1:bit_end]

    tag, rsa_start, rsa_end, _ = read_tlv(rsa, 0)
    if tag != 0x30 or rsa_end != len(rsa):
        raise ValueError("Invalid RSA public key")

    tag, n_start, n_end, pos = read_tlv(rsa, rsa_start)
    if tag != 0x02:
        raise ValueError("Missing RSA modulus")
    modulus = int.from_bytes(rsa[n_start:n_end], "big")

    tag, e_start, e_end, _ = read_tlv(rsa, pos)
    if tag != 0x02:
        raise ValueError("Missing RSA exponent")
    exponent = int.from_bytes(rsa[e_start:e_end], "big")
    return exponent, modulus


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


e, modulus = read_public_key("pubkey.pem")
if e != 3:
    raise ValueError("Unexpected RSA exponent")

with open("key.enc", "r", encoding="ascii") as f:
    encrypted_key = int(f.read().strip())

key = integer_cube_root(encrypted_key + modulus)
if key ** 3 != encrypted_key + modulus:
    raise ValueError("RSA ciphertext does not yield an exact cube")

with open("file.enc", "rb") as f:
    ciphertext = base64.b64decode(f.read())

key_bytes = key.to_bytes(len(ciphertext), "big")
plaintext = bytes(a ^ b for a, b in zip(ciphertext, key_bytes))
print(plaintext.decode("utf-8"))
