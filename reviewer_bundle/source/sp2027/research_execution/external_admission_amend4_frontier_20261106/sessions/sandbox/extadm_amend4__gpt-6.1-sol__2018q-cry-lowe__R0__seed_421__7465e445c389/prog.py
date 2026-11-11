import base64
import re


def read_tlv(data, pos=0):
    tag = data[pos]
    pos += 1
    length = data[pos]
    pos += 1
    if length & 128:
        count = length & 127
        if count == 0:
            raise ValueError('Invalid DER length')
        length = int.from_bytes(data[pos:pos + count], 'big')
        pos += count
    end = pos + length
    if end > len(data):
        raise ValueError('Truncated DER')
    return tag, data[pos:end], end


def cube_root(value):
    x = 1 << ((value.bit_length() + 2) // 3)
    while True:
        nxt = (2 * x + value // (x * x)) // 3
        if nxt >= x:
            break
        x = nxt
    while x ** 3 > value:
        x -= 1
    while (x + 1) ** 3 <= value:
        x += 1
    return x


def main():
    with open('pubkey.pem', 'r', encoding='ascii') as f:
        pem = f.read()
    encoded = ''.join(line.strip() for line in pem.splitlines()
                      if line.strip() and not line.startswith('-----'))
    der = base64.b64decode(encoded)
    tag, outer, end = read_tlv(der)
    assert tag == 0x30 and end == len(der)
    tag, algorithm, pos = read_tlv(outer)
    assert tag == 0x30
    tag, bits, end = read_tlv(outer, pos)
    assert tag == 0x03 and bits[0] == 0 and end == len(outer)
    tag, rsa, end = read_tlv(bits[1:])
    assert tag == 0x30 and end == len(bits) - 1
    tag, modulus_bytes, pos = read_tlv(rsa)
    assert tag == 0x02
    tag, exponent_bytes, end = read_tlv(rsa, pos)
    assert tag == 0x02 and end == len(rsa)
    modulus = int.from_bytes(modulus_bytes, 'big')
    exponent = int.from_bytes(exponent_bytes, 'big')
    assert exponent == 3

    with open('key.enc', 'r', encoding='ascii') as f:
        encrypted_key = int(f.read().strip())
    with open('file.enc', 'rb') as f:
        ciphertext = base64.b64decode(f.read())

    target = encrypted_key + modulus
    key_integer = cube_root(target)
    assert key_integer ** 3 == target
    assert pow(key_integer, exponent, modulus) == encrypted_key
    assert len(ciphertext) == 64
    key_bytes = key_integer.to_bytes(64, 'big')
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, key_bytes))

    match = re.search(rb'[A-Za-z][A-Za-z0-9_]*\{[^{}\r\n]*\}', plaintext)
    answer = match.group(0) if match else plaintext.rstrip(b'\x00 \t\r\n')
    text = answer.decode('utf-8')
    assert '\n' not in text and '\r' not in text
    print(text)


if __name__ == '__main__':
    main()
