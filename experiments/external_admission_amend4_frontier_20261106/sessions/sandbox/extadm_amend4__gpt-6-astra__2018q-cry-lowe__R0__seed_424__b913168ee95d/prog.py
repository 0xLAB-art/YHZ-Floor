import base64
import re


def read_tlv(data, pos=0):
    tag = data[pos]
    pos += 1
    length = data[pos]
    pos += 1
    if length & 0x80:
        count = length & 0x7f
        if count == 0:
            raise ValueError('Indefinite DER length')
        length = int.from_bytes(data[pos:pos + count], 'big')
        pos += count
    end = pos + length
    if end > len(data):
        raise ValueError('Truncated DER')
    return tag, data[pos:end], end


def integer_cube_root(n):
    x = 1 << ((n.bit_length() + 2) // 3)
    while True:
        next_x = (2 * x + n // (x * x)) // 3
        if next_x >= x:
            return x
        x = next_x


def main():
    with open('pubkey.pem', 'r', encoding='ascii') as f:
        body = ''.join(line.strip() for line in f if not line.startswith('-----'))
    der = base64.b64decode(body, validate=True)
    tag, spki, _ = read_tlv(der)
    assert tag == 0x30
    _, _, pos = read_tlv(spki)
    tag, bits, _ = read_tlv(spki, pos)
    assert tag == 0x03 and bits[0] == 0
    tag, rsa, _ = read_tlv(bits, 1)
    assert tag == 0x30
    tag, modulus, pos = read_tlv(rsa)
    assert tag == 0x02
    tag, exponent, _ = read_tlv(rsa, pos)
    assert tag == 0x02
    n = int.from_bytes(modulus, 'big')
    e = int.from_bytes(exponent, 'big')
    assert e == 3

    with open('key.enc', 'r', encoding='ascii') as f:
        y = int(f.read().strip())
    with open('file.enc', 'rb') as f:
        ciphertext = base64.b64decode(b''.join(f.read().split()), validate=True)

    assert 0 <= y < n
    k = integer_cube_root(y + n)
    assert k ** 3 == y + n
    assert pow(k, e, n) == y
    assert len(ciphertext) == 64
    key = k.to_bytes(64, 'big')
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, key))

    match = re.search(rb'flag\{[^{}\r\n]*\}', plaintext, re.IGNORECASE)
    answer = match.group(0) if match else plaintext.rstrip(b'\x00 \t\r\n')
    text = answer.decode('utf-8')
    if '\n' in text or '\r' in text:
        raise ValueError('Answer is not a single line')
    print(text)


if __name__ == '__main__':
    main()
