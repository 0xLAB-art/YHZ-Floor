import base64
import re


def tlv(data, offset=0):
    tag = data[offset]
    offset += 1
    length = data[offset]
    offset += 1
    if length & 0x80:
        count = length & 0x7f
        assert count > 0
        length = int.from_bytes(data[offset:offset + count], 'big')
        offset += count
    end = offset + length
    assert end <= len(data)
    return tag, data[offset:end], end


def exact_cube_root(value):
    low = 0
    high = 1 << ((value.bit_length() + 2) // 3)
    while low < high:
        middle = (low + high) // 2
        if middle ** 3 < value:
            low = middle + 1
        else:
            high = middle
    assert low ** 3 == value, 'Expected an exact cube'
    return low


with open('pubkey.pem', 'rb') as f:
    pem = f.read()
payload = b''.join(line.strip() for line in pem.splitlines()
                   if not line.startswith(b'-----'))
der = base64.b64decode(payload, validate=True)
tag, outer, end = tlv(der)
assert tag == 0x30 and end == len(der)
_, _, position = tlv(outer)
tag, bit_string, _ = tlv(outer, position)
assert tag == 0x03 and bit_string[0] == 0
 tag_placeholder = None
