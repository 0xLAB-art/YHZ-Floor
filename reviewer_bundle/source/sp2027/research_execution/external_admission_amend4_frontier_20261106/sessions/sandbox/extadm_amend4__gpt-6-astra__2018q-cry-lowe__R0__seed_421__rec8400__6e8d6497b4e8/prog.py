import base64
import re
import sys


def tlv(data, pos=0):
    tag = data[pos]
    pos += 1
    length = data[pos]
    pos += 1
    if length & 128:
        count = length & 127
        if not count:
            raise ValueError('Indefinite DER length')
        length = int.from_bytes(data[pos:pos + count], 'big')
        pos += count
    end = pos + length
    if end > len(data):
        raise ValueError('Truncated DER')
    return tag, data[pos:end], end


def cube_root(n):
    low = 0
    high = 1 << ((n.bit_length() + 2) // 3)
    while high - low > 1:
        mid = (low + high) // 2
        if mid * mid * mid <= n:
            low = mid
        else:
            high = mid
    return low


with open('pubkey.pem', 'r', encoding='ascii') as f:
    pem = ''.join(line.strip() for line in f if not line.startswith('-----'))
der = base64.b64decode(pem, validate=True)
_, outer, _ = tlv(der)
_, _, pos = tlv(outer)
tag, bit_string, _ = tlv(outer, pos)
if tag != 3 or bit_string[0] != 0:
    raise ValueError('Invalid public-key bit string')
_, rsa, _ = tlv(bit_string[1:])
_, modulus_bytes, pos = tlv(rsa)
_, exponent_bytes, _ = tlv(rsa, pos)
n = int.from_bytes(modulus_bytes, 'big')
e = int.from_bytes(exponent_bytes, 'big')
if e != 3:
    raise ValueError('Expected exponent three')

with open('key.enc', 'r', encoding='ascii') as f:
    y = int(f.read().strip())
with open('file.enc', 'r', encoding='ascii') as f:
    ciphertext = base64.b64decode(''.join(f.read().split()), validate=True)

k = cube_root(y + n)
if k * k * k != y + n:
    raise ValueError('RSA ciphertext plus modulus is not a perfect cube')
if len(ciphertext) != 64:
    raise ValueError('Expected a 64-byte ciphertext')

key = k.to_bytes(64, 'big')
plaintext = bytes(c ^ b for c, b in zip(ciphertext, key))
match = re.search(rb'flag\{[^{}\r\n]*\}', plaintext, re.IGNORECASE)
answer = match.group(0) if match else plaintext.strip(b'\x00 \t\r\n')
text = answer.decode('utf-8')
if '\n' in text or '\r' in text:
    raise ValueError('Recovered answer is not one line')
sys.stdout.write(text + '\n')
