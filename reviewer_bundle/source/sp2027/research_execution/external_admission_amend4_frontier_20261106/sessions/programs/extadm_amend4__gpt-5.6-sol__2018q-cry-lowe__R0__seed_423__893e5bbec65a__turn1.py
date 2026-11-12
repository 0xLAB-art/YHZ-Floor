import base64


def read_tlv(data, offset):
    tag = data[offset]
    offset += 1
    length = data[offset]
    offset += 1
    if length & 0x80:
        count = length & 0x7f
        length = int.from_bytes(data[offset:offset + count], "big")
        offset += count
    return tag, offset, offset + length


def load_modulus(path):
    with open(path, "r", encoding="ascii") as f:
        pem = f.read()
    body = "".join(line.strip() for line in pem.splitlines()
                   if not line.startswith("-----"))
    der = base64.b64decode(body)

    tag, outer_start, outer_end = read_tlv(der, 0)
    if tag != 0x30:
        raise ValueError("Invalid public key")

    tag, algorithm_start, algorithm_end = read_tlv(der, outer_start)
    if tag != 0x30:
        raise ValueError("Invalid algorithm identifier")

    tag, bit_start, bit_end = read_tlv(der, algorithm_end)
    if tag != 0x03 or der[bit_start] != 0:
        raise ValueError("Invalid RSA key bit string")

    rsa = der[bit_start + 1:bit_end]
    tag, sequence_start, sequence_end = read_tlv(rsa, 0)
    if tag != 0x30:
        raise ValueError("Invalid RSA public key")

    tag, modulus_start, modulus_end = read_tlv(rsa, sequence_start)
    if tag != 0x02:
        raise ValueError("Missing RSA modulus")
    modulus = int.from_bytes(rsa[modulus_start:modulus_end], "big")

    tag, exponent_start, exponent_end = read_tlv(rsa, modulus_end)
    if tag != 0x02:
        raise ValueError("Missing RSA exponent")
    exponent = int.from_bytes(rsa[exponent_start:exponent_end], "big")
    if exponent != 3:
        raise ValueError("Unexpected RSA exponent")

    return modulus


def integer_cube_root(n):
    x = 1 << ((n.bit_length() + 2) // 3)
    while True:
        y = (2 * x + n // (x * x)) // 3
        if y >= x:
            break
        x = y
    while (x + 1) ** 3 <= n:
        x += 1
    while x ** 3 > n:
        x -= 1
    return x


N = load_modulus("pubkey.pem")
with open("key.enc", "r", encoding="ascii") as f:
    Y = int(f.read().strip())

K = integer_cube_root(Y + N)
if K ** 3 != Y + N:
    raise ValueError("Y + N is not a perfect cube")

with open("file.enc", "rb") as f:
    ciphertext = base64.b64decode(f.read())

key = K.to_bytes(64, "big")
if len(ciphertext) != len(key):
    raise ValueError("Unexpected ciphertext length")

secret = bytes(a ^ b for a, b in zip(ciphertext, key))
print(secret.decode("utf-8"))
